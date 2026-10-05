import json
import platform
from dataclasses import dataclass, replace
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy
from scipy.optimize import linprog
from scipy.sparse import lil_matrix


@dataclass(frozen=True)
class Instance:
    name: str
    demand: tuple = (0.0, 4.0, 4.0)
    shared_capacity: tuple = (4.0, 4.0, 4.0)
    rail_capacity: tuple = (4.0, 4.0, 4.0)
    road_capacity: tuple = (4.0, 4.0, 4.0)
    max_buffer: float = 0.0
    budget: float = 4.0
    fixed_reservation: float | None = None
    source_stock: float = 20.0
    destination_stock: float = 0.0
    buffer_cost: float = 3.0
    reservation_fee: float = 1.0
    rail_cost: float = 1.0
    road_cost: float = 2.0
    backlog_penalty: float = 20.0
    final_backlog_penalty: float = 20.0
    storage_limit: float = 100.0


def solve(instance):
    horizon = len(instance.demand)
    if any(len(values) != horizon for values in (
        instance.shared_capacity, instance.rail_capacity, instance.road_capacity
    )):
        raise ValueError("Capacity trajectories must match the horizon")
    quantities = (*instance.demand, *instance.shared_capacity, *instance.rail_capacity,
                  *instance.road_capacity, instance.max_buffer, instance.budget,
                  instance.source_stock, instance.destination_stock, instance.buffer_cost,
                  instance.reservation_fee, instance.rail_cost, instance.road_cost,
                  instance.backlog_penalty, instance.final_backlog_penalty, instance.storage_limit)
    if not all(np.isfinite(value) and value >= 0 for value in quantities):
        raise ValueError("Instance quantities must be finite and nonnegative")
    if instance.fixed_reservation is not None and not (0 <= instance.fixed_reservation <= 4):
        raise ValueError("Fixed reservation must be between zero and four")
    variable_keys = [("buffer",), ("reservation",)]
    variable_keys.extend(("inventory", node, period) for node in ("source", "destination")
                         for period in range(horizon))
    variable_keys.extend((kind, period) for kind in ("backlog", "fulfillment")
                         for period in range(horizon))
    variable_keys.extend(("flow", mode, period) for mode in ("rail", "road")
                         for period in range(horizon - 1))
    positions = {key: position for position, key in enumerate(variable_keys)}
    costs = np.zeros(len(variable_keys))
    bounds = [(0.0, None) for key in variable_keys]
    costs[positions[("buffer",)]] = instance.buffer_cost
    costs[positions[("reservation",)]] = instance.reservation_fee
    bounds[positions[("buffer",)]] = (0.0, instance.max_buffer)
    reservation_bounds = (0.0, 4.0) if instance.fixed_reservation is None else (
        instance.fixed_reservation, instance.fixed_reservation
    )
    bounds[positions[("reservation",)]] = reservation_bounds
    for period in range(horizon):
        costs[positions[("backlog", period)]] = instance.backlog_penalty
        for node in ("source", "destination"):
            bounds[positions[("inventory", node, period)]] = (0.0, instance.storage_limit)
    costs[positions[("backlog", horizon - 1)]] += instance.final_backlog_penalty
    for period in range(horizon - 1):
        costs[positions[("flow", "rail", period)]] = instance.rail_cost
        costs[positions[("flow", "road", period)]] = instance.road_cost
        bounds[positions[("flow", "rail", period)]] = (0.0, instance.rail_capacity[period])
        bounds[positions[("flow", "road", period)]] = (0.0, instance.road_capacity[period])
    equalities = []
    equality_rhs = []
    inequalities = []
    inequality_rhs = []

    def add_equality(coefficients, rhs):
        equalities.append(coefficients)
        equality_rhs.append(rhs)

    def add_inequality(coefficients, rhs):
        inequalities.append(coefficients)
        inequality_rhs.append(rhs)

    add_inequality({("buffer",): instance.buffer_cost,
                    ("reservation",): instance.reservation_fee}, instance.budget)
    add_inequality({("buffer",): 1.0}, instance.storage_limit - instance.destination_stock)
    if instance.source_stock > instance.storage_limit:
        raise ValueError("Initial source stock exceeds storage")
    for period in range(horizon):
        source_row = {("inventory", "source", period): 1.0}
        destination_row = {("inventory", "destination", period): 1.0,
                           ("fulfillment", period): 1.0}
        if period == 0:
            source_rhs = instance.source_stock
            destination_row[("buffer",)] = -1.0
            destination_rhs = instance.destination_stock
        else:
            source_row[("inventory", "source", period - 1)] = -1.0
            destination_row[("inventory", "destination", period - 1)] = -1.0
            source_rhs = 0.0
            destination_rhs = 0.0
            for mode in ("rail", "road"):
                destination_row[("flow", mode, period - 1)] = -1.0
            receiving_row = {("inventory", "destination", period - 1): 1.0}
            receiving_row.update({("flow", mode, period - 1): 1.0 for mode in ("rail", "road")})
            add_inequality(receiving_row, instance.storage_limit)
        if period < horizon - 1:
            source_row.update({("flow", mode, period): 1.0 for mode in ("rail", "road")})
            add_inequality({("flow", "rail", period): 1.0,
                            ("flow", "road", period): 1.0}, instance.shared_capacity[period])
            add_inequality({("flow", "road", period): 1.0,
                            ("reservation",): -1.0}, 0.0)
        add_equality(source_row, source_rhs)
        add_equality(destination_row, destination_rhs)
        backlog_row = {("backlog", period): 1.0, ("fulfillment", period): 1.0}
        if period > 0:
            backlog_row[("backlog", period - 1)] = -1.0
        add_equality(backlog_row, instance.demand[period])

    def sparse_matrix(rows):
        matrix = lil_matrix((len(rows), len(variable_keys)))
        for row_number, coefficients in enumerate(rows):
            for key, value in coefficients.items():
                matrix[row_number, positions[key]] = value
        return matrix.tocsr()

    equality_matrix = sparse_matrix(equalities)
    inequality_matrix = sparse_matrix(inequalities)
    start = perf_counter()
    solution = linprog(costs, A_ub=inequality_matrix, b_ub=inequality_rhs,
                       A_eq=equality_matrix, b_eq=equality_rhs, bounds=bounds, method="highs")
    runtime = perf_counter() - start
    if not solution.success:
        raise RuntimeError(f"{instance.name}: {solution.message}")
    solution.x[np.abs(solution.x) < 1e-9] = 0.0
    equality_error = float(np.max(np.abs(equality_matrix @ solution.x - equality_rhs)))
    inequality_error = float(np.max(np.maximum(inequality_matrix @ solution.x - inequality_rhs, 0)))
    bound_error = max(max(lower - solution.x[position], 0.0,
                          solution.x[position] - upper if upper is not None else 0.0)
                      for position, (lower, upper) in enumerate(bounds))
    if max(equality_error, inequality_error, bound_error) > 1e-7:
        raise RuntimeError("Returned solution violates the instance constraints")
    decisions = {str(key): float(solution.x[position]) for key, position in positions.items()}
    return {
        "case": instance.name,
        "evidence_type": "synthetic deterministic verification; not a corridor result",
        "buffer": float(solution.x[positions[("buffer",)]]),
        "reservation": float(solution.x[positions[("reservation",)]]),
        "backlog": [float(solution.x[positions[("backlog", period)]]) for period in range(horizon)],
        "fulfillment": [float(solution.x[positions[("fulfillment", period)]]) for period in range(horizon)],
        "delay_burden": float(sum(solution.x[positions[("backlog", period)]] for period in range(horizon))),
        "final_backlog": float(solution.x[positions[("backlog", horizon - 1)]]),
        "objective": float(solution.fun),
        "status": solution.message,
        "runtime_seconds": runtime,
        "variable_count": len(variable_keys),
        "equality_count": len(equalities),
        "inequality_count": len(inequalities),
        "maximum_constraint_violation": max(equality_error, inequality_error, bound_error),
        "decisions": decisions,
    }


def require_close(actual, expected, description):
    if not np.allclose(actual, expected, atol=1e-7, rtol=0):
        raise RuntimeError(f"Verification failed: {description}: {actual} != {expected}")


def main():
    normal = Instance("Normal operations")
    rail_failure = replace(normal, name="Rail failure, road access", rail_capacity=(0.0, 0.0, 0.0))
    closed = replace(normal, name="Shared closure, no buffer", shared_capacity=(0.0, 0.0, 0.0))
    closed_reserved = replace(closed, name="Shared closure, fixed reservation", fixed_reservation=4.0)
    closed_buffer = replace(closed, name="Shared closure, buffer permitted", max_buffer=8.0, budget=24.0)
    bottleneck = replace(normal, name="Partial shared bottleneck", shared_capacity=(2.0, 2.0, 2.0))
    lead_time = replace(normal, name="Positive lead time", demand=(4.0, 0.0, 0.0))
    instances = (normal, rail_failure, closed, closed_reserved, closed_buffer, bottleneck, lead_time)
    outputs = [solve(instance) for instance in instances]
    require_close(outputs[0]["delay_burden"], 0.0, "normal service")
    require_close(outputs[0]["buffer"], 0.0, "normal buffer")
    require_close(outputs[0]["reservation"], 0.0, "normal reservation")
    require_close(outputs[1]["reservation"], 4.0, "surviving road access reservation")
    require_close(outputs[1]["delay_burden"], 0.0, "road substitutes for failed rail")
    require_close(outputs[2]["backlog"], [0.0, 4.0, 8.0], "closure backlog")
    require_close(outputs[3]["backlog"], outputs[2]["backlog"], "reservation cannot bypass closure")
    require_close(outputs[4]["buffer"], 8.0, "inventory covers isolated demand")
    require_close(outputs[4]["delay_burden"], 0.0, "buffer service")
    require_close(outputs[5]["backlog"], [0.0, 2.0, 4.0], "partial resource limit")
    require_close(outputs[5]["reservation"], 0.0, "reservation cannot enlarge shared capacity")
    require_close(outputs[6]["fulfillment"], [0.0, 4.0, 0.0], "no delivery before arrival")
    relaxed = solve(replace(closed_buffer, name="Larger feasible budget", budget=30.0))
    if relaxed["objective"] > outputs[4]["objective"] + 1e-7:
        raise RuntimeError("Larger feasible budget worsened the optimal objective")
    output_directory = Path("results/verification")
    output_directory.mkdir(parents=True, exist_ok=True)
    report = {"python_version": platform.python_version(), "scipy_version": scipy.__version__,
              "scope": "Two-node, two-service LP restriction with known deterministic capacities; no rolling or stochastic policy implemented",
              "cases": outputs, "additional_budget_check": relaxed}
    (output_directory / "model_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    table = [r"\begin{tabularx}{\textwidth}{Yrrrr}", r"\toprule",
             r"Synthetic check & Buffer & Reserved & Delay & Final backlog \\", r"\midrule"]
    for output in outputs:
        table.append(f"{output['case']} & {output['buffer']:.0f} & {output['reservation']:.0f} & "
                     f"{output['delay_burden']:.0f} & {output['final_backlog']:.0f} " + r"\\")
    table.extend([r"\bottomrule", r"\end{tabularx}", ""])
    (output_directory / "model_checks.tex").write_text("\n".join(table))
    print(f"Verified {len(outputs)} hand-checkable cases and one budget-monotonicity check.")
    for output in outputs:
        print(f"{output['case']}: delay={output['delay_burden']:.0f}, "
              f"buffer={output['buffer']:.0f}, reserved={output['reservation']:.0f}")


if __name__ == "__main__":
    main()