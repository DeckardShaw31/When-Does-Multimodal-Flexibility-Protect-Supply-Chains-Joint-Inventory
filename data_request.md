# Data and decisions needed to complete the manuscript

The manuscript now adopts a public-data-calibrated Los Angeles–Chicago container corridor. Official POLA 2024 aggregate observations have been summarized, and a small deterministic model restriction has been verified. The full corridor/scenario model and policy results remain unfinished. No publication outcome or empirical benefit is assumed. See `public_data_strategy.md` for source checks and corrections to unsupported strategic claims.

## 1. What I need from you now

Your study-direction answers have been accepted with the evidence boundaries in `public_data_strategy.md`. You do not need to answer the original case-selection questions again.

1. **Literature audit (completed October 4, 2026):** All six full-text PDFs in `papers/` have been verified and audited at the feature level in `literature_audit.csv`. The audit supports a narrow joint-feature distinction within this six-paper set; it does not establish a field-wide first.
2. **Public regional flow file (partially completed October 4, 2026):** FAF5.7.1 documentation and a user-prepared Los Angeles–Chicago selected-record CSV are present. `src/check_faf_data.py` verifies schema, arithmetic, checksum, and coverage. It finds 28 of 72 declared-scope combinations and does not independently reproduce row values from an official archive. The resulting composition percentages are not corridor modal shares.
3. **Optional useful evidence:** Applicable intact-container rail service schedules, documented travel times, public tariffs, or follow-up notices on the January 2023 Los Angeles–Chicago ingate suspension. These can be PDFs or browser-saved documents. Do not pay for a proprietary rate product or request confidential waybill records at this stage.
4. **Before choosing the final journal:** Confirm whether either JCR Q1 or SJR Q1 is sufficient, or both are required, and which reporting year/categories your institution uses. The supplied impact-factor figures and Q1 assertions have not been adopted as verified facts.

You do **not** need to code. Existing commands are `python src/check_public_data.py`, `python src/check_faf_data.py`, `python src/check_literature_audit.py`, and `python src/verify_model.py`; they have all been verified. The literature script checks file identity and supporting text markers, not automated absence claims. The model script checks a synthetic deterministic restriction only, not the full stochastic study.

## 2. Minimum data package

Provide whatever is available in CSV, Excel, anonymized documents, or links. Partial records are useful. Leave unknown values blank rather than guessing; estimates are acceptable when explicitly labeled.

| Priority | Data | What to ask for |
|---|---|---|
| Essential | Feasible services | Origins, destinations, modes, lead times, timetables, transfer requirements |
| Essential | Demand and initial stock | Destination demand by date, baseline stock, storage limits |
| Essential | Usable capacity | Per-period carrier access, physical service limits, shared terminal handling limits, background commitments |
| Essential | Costs and contracts | Buffer delivered cost, reservation fee, activation charge, spot rate/access, priority and failure conditions |
| Essential | Disruption description | Affected services/facilities, onset, capacity loss, restoration trajectory, common-event identifier |
| Important | Source availability | Gateway arrivals and initially in-transit shipments, rather than unlimited replenishment |
| Important | Service valuation | Delay consequences, final-backlog treatment, and whether demand is backordered or lost |
| Optional | Emission factors | Consistent mode-specific factors and units, only for a later secondary analysis |

A useful first extract is normal operating records plus one documented disruption, if available. Longer history and additional independent events improve calibration and evaluation, but there is no universal minimum record count that guarantees adequate evidence. If historical events are too few, we will separate observed case checks from explicit scenario stress tests.

## 3. Empty CSV templates

The files in `data/templates/` contain headers only. They are **not** synthetic observations or downloaded datasets. Add rows only when evidence or a documented assumption exists. Do not put confidential data in a public/shared location without permission.

| File | Row definition |
|---|---|
| `nodes.csv` | One operational node/state; use separate waiting and ready states for terminal processing |
| `services.csv` | One movement or processing arc; record current access and contract semantics separately from physical capacity |
| `resource_usage.csv` | One arc/shared-resource relationship |
| `resources.csv` | One shared facility/resource and its normal residual capacity |
| `demand.csv` | One destination/date demand observation |
| `source_arrivals.csv` | One source/date availability observation |
| `disruptions.csv` | One event/date/affected-asset state, repeated across recovery dates and affected resources |
| `provenance.csv` | One parameter/source/assumption record with status, units, and uncertainty bounds |

### Template conventions

- Use consistent IDs across files, an ISO date (`YYYY-MM-DD`), one freight unit, and one period length.
- State whether capacity is installed, observed throughput, or residual usable capacity. These are not interchangeable.
- `delivered_buffer_cost_per_unit` includes procurement and pre-event positioning. For non-demand nodes it can be blank; extra destination buffers are the first model's scope.
- `reservation_fee_per_unit_per_horizon` purchases one unit of per-period access throughout the stated contract horizon. Distinguish it from `reserved_activation_cost_per_unit`, which applies only when freight moves.
- `arc_kind` is `movement` or `processing`. A processing arc connects waiting and ready node states.
- `lead_time_periods` must be positive in the initial model. Timetable details can be supplied as a separate document or schedule table if needed.
- Resource consumption applies at dispatch/processing start in the first model. Resource occupancy over several periods needs a more detailed representation.
- `capacity_fraction`, `base_access_fraction`, `spot_access_fraction`, and `reserved_usable_fraction` lie between 0 and 1 relative to stated nominal values. A closed asset has zero physical capacity even when a reservation exists.
- In `disruptions.csv`, `asset_type` is `service` or `resource`; `event_id` links jointly affected assets. Use dated recovery rows, not just a final duration.
- `evidence_status` is `observed`, `estimated`, `expert_elicited`, or `assumed`.
- Record currency and price year in the relevant provenance rows; do not silently mix currencies.
- Initial in-transit shipments require a separate shipment/arrival table if relevant. The source template is not a substitute for that state.
- The first data import will validate schema and units; these headers are a starting collection format, not a finalized database specification.

## 4. Selected public-data route

We are preparing a public-data-calibrated computational study without a private partner dependency. Use documented service geography and public aggregate flows for scale, and represent private contract/stock parameters as explicitly stated ranges. This can support controlled mechanism tests, but it must not be described as a validated company operating policy or as fully observed shipper operations.

The POLA 2024 monthly subset has already been transcribed from the official table and checked against annual sums. It contains all-commodity aggregate port observations, not Chicago-bound shipper demand. The FAF5.7.1 selected-record CSV is useful for testing the processing workflow but requires an official archive or saved DTT query for row-level provenance and complete filtering. FAF mode 5 is Multiple Modes & Mail, not an observed intermodal-rail category. STB public revenue may be masked; ATRI operating cost is not a shipper tariff. Reservation terms, inventory, usable daily capacity, and restoration trajectories remain assumptions unless compatible evidence becomes available.

## 5. Literature audit status

The following full texts are present and have been audited. The corrected feature boundaries are recorded in `literature_audit.csv`.

1. Aldrighetti, Battini, and Ivanov: resilience portfolios, DOI `10.1016/j.omega.2023.102841`.
2. Hasani Goodarzi and colleagues: resilient/sustainable intermodal planning, DOI `10.1007/s10668-024-05549-7`.
3. Guo and colleagues: multi-period routing and storage, DOI `10.1016/j.cor.2024.106676`.
4. Rahiminia and colleagues: sustainable intermodal planning under mixed uncertainty, DOI `10.1016/j.seps.2024.102146`.
5. Wang and colleagues: resilient multimodal service pricing and capacity planning, DOI `10.1016/j.tre.2026.104774`.
6. Chen and Miller-Hooks: intermodal recovery capability, DOI `10.1287/trsc.1110.0376`.

Rahiminia et al. already include buffer inventory, terminal/link/storage capacities, mode switching, and disruption scenarios. Goodarzi et al. include event scenarios that may affect multiple locations. Wang et al. include advance arc-capacity rental. Therefore, the defensible candidate contribution is their joint interaction under a focal-shipper, shared-resource, sequential-recovery formulation. We must still conduct citation-chain and database searches through the actual search date.

## 6. Implementation status and next work

1. **Completed:** A sourced port subset, public-data consistency checks, and generated descriptive table.
2. **Completed:** A small deterministic LP restriction and seven hand-checkable cases plus one budget check; not a full corridor model.
3. **Completed with limits:** Six-paper feature audit and FAF selected-record workflow; official FAF row-level reproduction and broader novelty search remain pending.
4. **Pending:** Full network, processing queues, correlated scenarios, and information-consistent rolling controller.
5. **Pending:** Held-out policy comparisons, uncertainty, assumption sensitivity, and corridor results/discussion.
6. **Pending:** Final target-journal scope/ranking check and submission-format revision.

SciPy/HiGHS is available and no installation or outside computation is currently needed. To upgrade the FAF file from a user-prepared selected subset to a traceable extract, please upload the official archive used to create it or preserve/export the exact DTT query output and filter settings.

## 7. Adopted reply block

```text
Country/corridor: United States; POLA gateway to Chicago metropolitan market.
Commodity: Homogeneous nonperishable 40-foot containers; TEU flow units (2 TEU/box).
Access route: Public-data-calibrated computational study; no private partner required.
Prepared observations: POLA 2024 monthly loaded imports and total throughput.
Next data: Official FAF archive or saved DTT output/filter settings; service/lead-time evidence.
Unobserved operational inputs: Stock, reservations, residual capacity, recovery trajectories.
First venue candidate: TRE; EJOR/IJPE alternatives; ranking/year/category to verify.
Full texts: Six closest papers uploaded and audited; broader citation-chain/database search pending.
Schedule: Aspirational 12–16 weeks after novelty and data feasibility gates.
```