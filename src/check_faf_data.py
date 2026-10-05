import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd


SOURCE_PATH = Path("data/public/faf5_lac_extract.csv")
OUTPUT_DIRECTORY = Path("data/processed")
CURRENT_DATE = "2026-10-04"

DESTINATIONS = ("171", "181")
TRADE_TYPES = (1, 2)
MODES = (1, 2, 5)
COMMODITIES = (24, 30, 35, 39, 40, 43)
MODE_NAMES = {1: "Truck", 2: "Rail", 5: "Multiple modes & mail"}
TRADE_NAMES = {1: "Domestic", 2: "Import"}


def validate(data):
    required_columns = [
        "source_id", "release", "dms_orig", "dms_dest", "trade_type",
        "dms_mode", "sctg2", *[f"tons_{year}" for year in range(2017, 2025)],
        "value_2024", "tmiles_2024", "commodity_name",
    ]
    missing_columns = sorted(set(required_columns) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    if not (data["source_id"] == "FAF571").all():
        raise ValueError("Unexpected source identifier")
    if not (data["release"] == "5.7.1").all():
        raise ValueError("Unexpected release identifier")
    if not (data["dms_orig"] == "061").all():
        raise ValueError("Expected domestic origin 061")
    if not data["dms_dest"].isin(DESTINATIONS).all():
        raise ValueError("Unexpected destination code")
    if not data["trade_type"].isin(TRADE_TYPES).all():
        raise ValueError("Unexpected trade type")
    if not data["dms_mode"].isin(MODES).all():
        raise ValueError("Unexpected domestic mode")
    if not data["sctg2"].isin(COMMODITIES).all():
        raise ValueError("Unexpected SCTG code")
    key_columns = ["dms_orig", "dms_dest", "trade_type", "dms_mode", "sctg2"]
    if data.duplicated(key_columns).any():
        raise ValueError("Duplicate origin-destination-trade-mode-commodity record")
    numeric_columns = [f"tons_{year}" for year in range(2017, 2025)] + [
        "value_2024", "tmiles_2024"
    ]
    numeric = data[numeric_columns]
    if not np.isfinite(numeric).all().all():
        raise ValueError("Non-finite flow quantity")
    if (numeric < 0).any().any():
        raise ValueError("Negative flow quantity")


def coverage_audit(data):
    expected = set(itertools.product(DESTINATIONS, TRADE_TYPES, MODES, COMMODITIES))
    observed = set(zip(data["dms_dest"], data["trade_type"], data["dms_mode"], data["sctg2"]))
    missing = sorted(expected - observed)
    return {
        "declared_scope_combination_count": len(expected),
        "observed_combination_count": len(observed),
        "missing_combination_count": len(missing),
        "coverage_fraction": len(observed) / len(expected),
        "complete_factorial_coverage": not missing,
        "missing_combinations": [
            {"dms_dest": destination, "trade_type": trade, "dms_mode": mode, "sctg2": commodity}
            for destination, trade, mode, commodity in missing
        ],
    }


def write_latex(summary):
    composition = summary["selected_record_composition_2024"]
    assumptions = summary["illustrative_teu_equivalent"]
    coverage = summary["coverage_audit"]
    lines = [
        r"\begin{tabular}{lr}",
        r"\toprule",
        r"FAF5.7.1 selected-record diagnostic & Value \\",
        r"\midrule",
        f"Rows supplied & {summary['record_count']} " + r"\\",
        f"Declared-scope combinations represented & {coverage['observed_combination_count']}/"
        f"{coverage['declared_scope_combination_count']} " + r"\\",
        f"Sum of 2024 tonnage in supplied rows (thousand short tons) & "
        f"{summary['selected_record_totals_2024']['tonnage_ktons']:,.2f} " + r"\\",
        f"Mode 5 share within supplied rows & {composition['Multiple modes & mail'] * 100:.1f}" + r"\% \\",
        f"Truck share within supplied rows & {composition['Truck'] * 100:.1f}" + r"\% \\",
        f"Rail share within supplied rows & {composition['Rail'] * 100:.1f}" + r"\% \\",
        f"Import share within supplied rows & {summary['selected_record_trade_composition_2024']['Import'] * 100:.1f}" + r"\% \\",
        f"Illustrative TEU-equivalent/day at {assumptions['short_tons_per_teu']:.1f} short tons/TEU & "
        f"{assumptions['all_selected_tonnage_teu_equivalent_per_day']:,.1f} " + r"\\",
        f"Illustrative 1\\% scenario scale (TEU-equivalent/day) & "
        f"{assumptions['one_percent_scenario_scale_teu_equivalent_per_day']:,.1f} " + r"\\",
        r"\bottomrule",
        r"\end{tabular}",
        "",
    ]
    (OUTPUT_DIRECTORY / "faf5_lac_summary.tex").write_text("\n".join(lines))


def main():
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Missing extract file: {SOURCE_PATH}")
    data = pd.read_csv(SOURCE_PATH, dtype={"dms_orig": str, "dms_dest": str})
    validate(data)
    coverage = coverage_audit(data)
    total_tonnage = float(data["tons_2024"].sum())
    mode_tonnage = data.groupby("dms_mode")["tons_2024"].sum().to_dict()
    trade_tonnage = data.groupby("trade_type")["tons_2024"].sum().to_dict()
    short_tons_per_teu = 11.5
    equivalent_daily_teu = total_tonnage * 1000 / short_tons_per_teu / 366
    summary = {
        "source_id": "FAF571",
        "source_release": "5.7.1",
        "checked_date": CURRENT_DATE,
        "input_sha256": hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest(),
        "record_count": int(len(data)),
        "provenance_status": (
            "User-prepared selected-record CSV. Schema, arithmetic, checksum, and declared-scope coverage "
            "were checked locally; row values were not independently reproduced from an official FAF archive."
        ),
        "coverage_audit": coverage,
        "selected_record_totals_2024": {
            "tonnage_ktons": round(total_tonnage, 2),
            "value_millions_current_usd": round(float(data["value_2024"].sum()), 2),
            "ton_miles_millions": round(float(data["tmiles_2024"].sum()), 2),
        },
        "selected_record_composition_2024": {
            MODE_NAMES[mode]: round(float(mode_tonnage.get(mode, 0)) / total_tonnage, 4)
            for mode in MODES
        },
        "selected_record_trade_composition_2024": {
            TRADE_NAMES[trade]: round(float(trade_tonnage.get(trade, 0)) / total_tonnage, 4)
            for trade in TRADE_TYPES
        },
        "interpretation_limits": [
            "Composition percentages describe only the supplied rows because the declared origin-destination-trade-mode-commodity grid is incomplete.",
            "FAF mode 5 is Multiple Modes & Mail and is not identifiable as truck-rail intermodal or containerized freight.",
            "Import records with domestic origin 061 identify the Los Angeles zone of entry, not a specific seaport, terminal, or foreign arrival mode.",
            "The TEU calculation treats all selected tonnage as containerizable solely to define a scenario scale; it is not an observed container volume.",
        ],
        "illustrative_teu_equivalent": {
            "short_tons_per_teu": short_tons_per_teu,
            "containerization_fraction_assumed_for_equivalent": 1.0,
            "all_selected_tonnage_teu_equivalent_per_day": round(equivalent_daily_teu, 2),
            "one_percent_scenario_scale_teu_equivalent_per_day": round(equivalent_daily_teu * 0.01, 2),
        },
    }
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIRECTORY / "faf5_lac_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    pd.DataFrame(coverage["missing_combinations"]).to_csv(
        OUTPUT_DIRECTORY / "faf5_lac_missing_combinations.csv", index=False
    )
    write_latex(summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()