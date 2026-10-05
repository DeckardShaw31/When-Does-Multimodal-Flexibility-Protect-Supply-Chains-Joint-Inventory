# Selected case, source audit, and outstanding evidence

Updated October 4, 2026. This document supersedes the open case-selection questions in the initial plan. It does not confirm publication probability, full operational data access, or a completed literature audit.

## 1. Adopted scope

- **Study type:** Public-data-calibrated computational study, with transparent assumptions for private operational inputs.
- **Primary geography:** Port of Los Angeles to the Chicago metropolitan freight market. The broader San Pedro Bay context is relevant, but the initial public volume series is POLA only. Do not present it as combined POLA/POLB throughput.
- **Modes:** Direct road movement and road–rail intermodal alternatives. The Alameda Corridor is a rail connection, not a resource that all direct trucks physically traverse.
- **Facilities:** Aggregate marine-terminal operational states; a documented Southern California rail interface; alternative Chicago-area rail interfaces; three stylized customer zones. Carrier publications establish regional intermodal connections, not a currently available contract between every chosen pair of facilities.
- **Commodity:** A homogeneous, nonperishable 40-foot-container service class. Freight flows use TEU; one standardized 40-foot box equals two TEU. Full-container indivisibility is initially relaxed for aggregate planning. FAF commodity selection and containerization/weight assumptions remain to be specified.
- **Horizon:** Start with 30 operating days plus a lead-time/recovery tail, then examine 60 days. No claim of seconds-to-minutes performance before benchmarking.
- **First journal candidate:** Transportation Research Part E. EJOR and IJPE remain alternatives whose fit depends on the final methodological/economic contribution. Verify reporting year, subject category, and the institution's JCR/SJR requirement before asserting Q1 status; no impact-factor numbers are used here.
- **Deadline:** An aspirational 12–16-week draft schedule after the data/literature gates. It is not a guaranteed submission schedule.

## 2. Corrections to the supplied strategy

| Supplied assertion | Treatment in this project |
|---|---|
| Open data are 100% guaranteed and all inputs are available | Public aggregate observations exist; stock, reservation rights, daily residual capacities, rates, and recovery trajectories are still unobserved or access-dependent. |
| Over 80% of top-journal optimization papers use these data | No sampling study/source was provided. Excluded from the manuscript. |
| Private approvals always take 6–12 months | Not a verified general statistic; excluded. No private partner is required by our selected study design. |
| FAF5.6 is the prescribed current version | The BTS page checked October 4, 2026 identifies FAF5.7.1. Pin the actual downloaded version and year; do not silently mix releases. |
| Truck operating costs are freight rates | ATRI operating costs are cost benchmarks, not a lane-specific shipper quote. Add explicit utilization, empty mileage, markup, drayage, and handling assumptions. |
| Public rail waybill revenue supplies exact contracts | STB warns that public freight revenue may be masked. Do not infer confidential prices or reservations from it. |
| Road and rail necessarily share the same gate/crane | Verify resource incidence; separate road gates, rail lifts, and common upstream release. Partial sharing is an experimental variable, not a fact about every port facility. |
| All existing studies assume unconstrained fallback | Contradicted by prior capacity/disruption/recovery models. The novelty statement must be narrower and full-text audited. |
| Inventory is the only possible protection | Only under an explicitly closed downstream boundary without surviving bypass, local supply, or other recovery levers; committed in-transit/downstream stock can also protect service. |
| Goodarzi et al. appeared in Environmental Science and Pollution Research | The checked publisher record identifies Environment, Development and Sustainability, published March 12, 2025. |

## 3. Source register

URLs are lookup strings. Access checks used the web research tool. Direct bulk retrieval from the terminal was denied by this environment on October 4, 2026; no bulk FAF/STB archive has been downloaded. The port subset was transcribed from the official table, not obtained through an automated scraping script.

| ID | Source and checked content | Intended use | Critical restriction |
|---|---|---|---|
| POLA2024 | Official 2024 monthly container table | Loaded-import scale and monthly profile | All commodities and box sizes; not shipper demand, capacity, or corridor flow |
| FAF571 | BTS FAF5 page identifies release 5.7.1 and 2017–2024 regional estimates | Regional/commodity context; later filtered calibration | Thousands of tons are not TEU; 2024 estimates are preliminary; no daily firm orders |
| STBPUWS | STB Waybill page and public-data warning | Rail-flow context if accessible | Public revenue may be masked; no private reservation terms |
| ATRI2025 | ATRI economic-analysis page: 2024 average operating cost $2.260 per truck-mile, reported July 1, 2025 | Same-price-year trucking cost anchor | Industry average, not local drayage or customer tariff |
| ACTAHISTORY | ACTA describes a 20-mile rail connection between the ports and downtown Los Angeles | Rail topology context | Not a shared highway gate or shipper-capacity measurement |
| BNSFNETWORK | BNSF describes the Los Angeles–Chicago Southern Transcon and Hobart/Commerce/LPC facilities | Candidate regional service geography | Marketing description is not a dated booking entitlement or travel-time observation |
| UPNETWORK | UP facility map lists Southern California and Chicago facilities | Alternative interface geography | A facility's existence does not establish every assumed service connection |
| UP2023EVENT | UP notice dated January 24, 2023 reports January 23 mainline interruption and selected Los Angeles–Chicago ingate suspensions | Documented event motivation and affected-lane evidence | Notice is not a full daily physical-capacity/recovery trajectory; outgating was encouraged |
| EPAUNITS | EPA port-operations primer defines a 40-foot container as two TEU | Unit conversion | TEU does not fix cargo weight or number of lifts in a mixed-size system |

Lookup strings:

```text
POLA2024: https://portoflosangeles.org/business/statistics/container-statistics/historical-teu-statistics-2024
FAF571: https://www.bts.gov/faf/faf5
STBPUWS: https://www.stb.gov/reports-data/waybill/
ATRI2025: https://truckingresearch.org/about-atri/atri-research/economic-analysis/
ACTAHISTORY: https://www.acta.org/about/history/
BNSFNETWORK: https://www.bnsf.com/news-media/railtalk/service/intermodal-facilities.html
UPNETWORK: https://www.up.com/shipping/intermodal/intmap
UP2023EVENT: https://www.up.com/customers/announcements/premium/internationalintermodalterminals/PR2023-9.html
EPAUNITS: https://www.epa.gov/ports-initiative/ports-primer-31-port-operations
```

## 4. Public observations already prepared

`data/public/pola_2024_monthly.csv` contains only month, loaded imports, and total port TEU, transcribed from POLA's official 2024 table. `src/check_public_data.py` checks the published annual sums and derives a month-specific average per calendar day and a normalized import profile. The generated summary appears in the manuscript. A checksum records the local input used; it does not certify the source page or replace an archived download.

The 2024 base year aligns this port series with the ATRI 2025 report's 2024 cost benchmark. No use of a newer report's costs as if they were 2024 costs is planned.

These observations are **scale anchors**, not a complete operational dataset. Neither total TEU nor total imports measure available terminal capacity. Loaded imports should not be replaced with totals including exports and empties when constructing import demand.

## 5. Calibration rules

### Demand and commodity

Let `I_m` be observed loaded imports for month `m`, `days_m` the number of calendar days, `theta` an assumed target-commodity/container-service share, `chi` an assumed Chicago-bound share, and `sigma` an assumed focal-shipper share. A transparent illustrative demand scale is:

```text
daily_shipper_TEUs = I_m / days_m * theta * chi * sigma
```

None of `theta`, `chi`, and `sigma` is measured by the port table. Do not estimate them by dividing incompatible denominators across datasets. Use declared sensitivity ranges and record what evidence eventually supports them. Customer-zone allocations must sum to one. Daily variation and days-of-week effects are modeled assumptions unless supported by independent observations.

FAF can inform regional/commodity context after selecting codes and domestic/foreign-trade boundaries. Containerizing all FAF truck/rail tonnage is invalid. If using weight to infer TEU, record short-ton versus metric-ton units and an uncertain commodity-specific laden weight per TEU. The port and FAF routes are alternative or complementary scale checks, not independent demand quantities to add together.

### Costs

Use the 2024 ATRI benchmark as the carrier operating-cost component only. A road service cost may be represented as:

```text
cost_per_40ft_box = effective_truck_miles * operating_cost_per_mile
                  + handling_and_other_documented_costs
                  + explicitly_assumed_margin
cost_per_TEU = cost_per_40ft_box / 2
```

Effective mileage accounts for empty movement/utilization. Actual distance, drayage conditions, road/rail equipment compatibility, and direct movement of an intact marine container must be checked; transloading into domestic boxes changes the model boundary. Public tariffs may supply an applicable fee but do not automatically supply the full shipment price. Reservation fees and fulfillment fractions remain explicit assumptions.

### Capacity, processing, and dependencies

Construct residual usable capacity as a documented or assumed share of physical resources after background commitments. Do not convert observed average throughput directly into maximum daily capacity. For a homogeneous 40-foot-box processing operation with one lift per box, a resource measured in lifts has `gamma = 0.5 lifts/TEU`; other operations require their own coefficients.

Separate physical resource sharing from common-hazard exposure. The road and rail branches can have distinct gates/lifts while depending on the same upstream release or correlated hazard. Include a surviving bypass configuration so the paper does not hard-code its anticipated conclusion.

### Disruptions

The January 2023 UP notice establishes that specified ingates were suspended, not that all San Pedro Bay freight or all competing modes stopped. It is an event anchor only. Until subsequent notices/records establish recovery, restoration duration and residual capacities remain stress-test assumptions. The 2021–2022 congestion episode is a different operational regime, not interchangeable with a binary weather closure.

## 6. Resolved and partially resolved items (October 4, 2026)

- **Six-paper audit complete:** All six closest uploaded PDFs have been verified and audited at the feature level in `literature_audit.csv`. Rahiminia et al. already model buffer inventory and finite terminal/link/storage capacity; Goodarzi et al. use multi-location event scenarios; Wang et al. rent arc capacity in advance. Within this six-paper set, no single paper jointly models destination buffers, shipper-held transport access rights, a separate shared processing resource, common-cause exposure, and sequential recovery. A broader search is still required before any field-wide absence claim.
- **FAF5.7.1 workflow partially complete:** `data/public/faf5_metadata_documentation.md` documents official portals and boundaries. The uploaded CSV is a user-prepared 28-row selected subset. `src/check_faf_data.py` verifies its schema, arithmetic, checksum, and declared-scope coverage, finding 28 of 72 combinations. It does not independently reproduce row values from an official archive. Mode 5 is Multiple Modes & Mail and cannot be reported as intermodal rail; TEU values are illustrative equivalents only.

## 7. Next gates

1. Upload the official FAF archive used for the subset, or save/export the exact DTT result and filter settings; regenerate a complete traceable extract.
2. Complete citation-chain and database searches beyond the six uploaded closest papers.
3. Specify service feasibility and lead-time ranges from applicable carrier evidence (BNSF/UP and highway benchmarks).
4. Implement the shipper-scale network and rolling-horizon controller; benchmark actual computational size.
5. Run final held-out comparisons and write corridor findings.

The deterministic verification example introduced alongside this document checks code behavior only. It is not calibrated to Los Angeles, does not estimate historical losses, and is not evidence of a Q1 publication outcome.