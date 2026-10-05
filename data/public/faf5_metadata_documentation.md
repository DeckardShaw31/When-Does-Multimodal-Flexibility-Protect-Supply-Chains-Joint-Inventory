# Freight Analysis Framework Version 5.7.1 (FAF5.7.1): Data Documentation and Corridor Specification

**Prepared:** October 4, 2026
**Source Organization:** Bureau of Transportation Statistics (BTS), U.S. Department of Transportation & Federal Highway Administration (FHWA)  
**Host & Technical Repository:** Oak Ridge National Laboratory (ORNL) Center for Transportation Analysis  
**Release Identifier:** FAF5.7.1 (Updated with 2023 USACE waterborne statistics, improved foreign trade ground border points of entry, and preliminary 2024 estimates)  
**Official Portals:**
- BTS FAF5 Portal: `https://www.bts.gov/faf/faf5`
- ORNL-hosted FAF5 User Guide: `https://faf.ornl.gov/faf5/data/FAF5%20User%20Guide.pdf`
- ORNL FAF5 Repository & Data Tabulation Tool: `https://faf.ornl.gov/faf5/`

---

## 1. Archive Access and Download Registry

Direct automated curl/urllib downloads from terminal environments to US federal `.gov` endpoints frequently encounter HTTP 403 or TLS connection reset restrictions. Researchers can retrieve the official source archives directly via browser or institution network using the verified URLs below:

| Dataset / Component | Format | Verified URL | Role in Calibration |
|---|---|---|---|
| **FAF5.7.1 Regional Database (2018–2024)** | ZIP / CSV | `https://faf.ornl.gov/faf5/data/download_files/FAF5.7.1_2018-2024.zip` | Annual flow estimates and preliminary 2024 regional flows |
| **FAF5.7.1 Regional Base Year (2017)** | ZIP / CSV | `https://faf.ornl.gov/faf5/data/download_files/FAF5.7.1.zip` | Benchmark economic census baseline flows |
| **FAF5.7.1 Forecasts (2030–2050)** | ZIP / CSV | `https://faf.ornl.gov/faf5/data/download_files/FAF5.7.1_HiLoForecasts.zip` | Long-term macro growth trajectories |
| **FAF5 User Guide (Official PDF)** | PDF | `https://faf.ornl.gov/faf5/data/FAF5%20User%20Guide.pdf` | Schema, methodology, and zone boundary definitions; the hosted guide is labeled Release 5.1, while the ORNL portal identifies 5.7.1 as the current data release |
| **FAF5 Data Tabulation Tool (DTT)** | Web Tool | `https://faf.ornl.gov/faf5/dtt_total.aspx` | Interactive query tool for ODCM sub-matrices |
| **CFS Area Code / FAF5 Zone Lookup** | XLSX | `https://www.bts.gov/sites/bts.dot.gov/files/2021-02/CFS-area-code-FAF5-zone-id.xlsx` | Crosswalk between Census MSAs/CSAs and FAF numeric IDs |

---

## 2. Database Schema & Field Definitions

The regional origin-destination-commodity-mode (ODCM) database adheres to the following record layout:

| Field Name | Type | Description | Values / Units |
|---|---|---|---|
| `fr_orig` | Integer | Foreign origin region (for import movements) | Numeric code (e.g., 801 Canada, 802 Mexico, 803 Rest of World); blank/0 for domestic |
| `dms_orig` | String/Int | Domestic origin FAF zone code | 3-digit zone code (e.g., `061` = Los Angeles, CA) |
| `dms_dest` | String/Int | Domestic destination FAF zone code | 3-digit zone code (e.g., `171` = Chicago, IL Part) |
| `fr_dest` | Integer | Foreign destination region (for export movements) | Numeric code; blank/0 for domestic |
| `fr_inmode` | Integer | Foreign inbound mode of transport at port of entry | 1: Water, 2: Air, 3: Truck, 4: Rail, 5: Pipeline, 7: Other |
| `dms_mode` | Integer | Domestic mode of transport within the United States | 1: Truck, 2: Rail, 3: Water, 4: Air, 5: Multiple modes & mail, 6: Pipeline, 7: Other |
| `fr_outmode`| Integer | Foreign outbound mode of transport for exports | Mode code; blank/0 for domestic |
| `sctg2` | Integer | 2-digit Standard Classification of Transported Goods | Codes 01 through 43 (e.g., 35 = Electronics, 43 = Mixed freight) |
| `trade_type`| Integer | Direction and international classification of flow | 1: Domestic, 2: Import, 3: Export |
| `tons_YYYY` | Float | Annual freight weight in year YYYY | **Thousands of short tons** (1 thousand short tons = 2,000,000 lbs = 907.185 metric tons) |
| `value_YYYY`| Float | Annual shipment monetary value in year YYYY | **Millions of current U.S. dollars** |
| `tmiles_YYYY`| Float | Annual ton-miles generated in year YYYY | **Millions of ton-miles** |

---

## 3. Code Lookup Dictionaries for the Los Angeles–Chicago Corridor

### 3.1 Geographic Zones (`dms_orig`, `dms_dest`)
* **`061`**: **Los Angeles-Long Beach-Anaheim, CA CFS Area** (FAF Zone 061). Encompasses Los Angeles County and Orange County, including the Ports of Los Angeles and Long Beach (San Pedro Bay gateway) and near-dock intermodal railheads (LATC, Hobart, ICTF).
* **`171`**: **Chicago-Naperville, IL-IN-WI CFS Area (Illinois Part)** (FAF Zone 171). The primary freight consumption and logistics cluster in the Midwest, including major Class I intermodal yards (Corwith, BNSF Logistics Park Chicago, UP Global I/II/IV).
* **`181`**: **Chicago-Naperville, IL-IN-WI CFS Area (Indiana Part)** (FAF Zone 181). Adjacent industrial and logistics park submarket in northwest Indiana.

### 3.2 Domestic Transport Modes (`dms_mode`)
* **`1`: Truck**: Direct long-haul over-the-road trucking (for-hire truckload, LTL, and private fleets). Connects Southern California and Chicago via Interstate 40 / Interstate 10 / Interstate 55 (~2,015 to 2,100 highway miles).
* **`2`: Rail**: Conventional rail carload and dedicated unit train movements.
* **`5`: Multiple modes & mail**: Shipments reported as using multiple modes, parcel delivery, USPS, or courier services. The FAF guide explicitly states that this category is not limited to containerized or trailer-on-flatcar shipments. It therefore cannot be relabeled as intermodal rail without an additional source.

### 3.3 Target Commodity Classes (`sctg2`)
For nonperishable, container-compatible consumer and manufactured freight:
* **`24`**: Plastics and articles thereof; rubber and articles thereof.
* **`30`**: Textiles, leather, apparel, and finished textile articles.
* **`35`**: Electronic and electrical equipment, office equipment, computing machinery.
* **`39`**: Furniture, lamps, lighting fittings, prefabricated buildings.
* **`40`**: Miscellaneous manufactured products (toys, games, sporting equipment).
* **`43`**: Mixed freight (consolidated consumer retail goods, multi-commodity distribution shipments).

---

## 4. Calibration Rules and Conversion Protocol

### 4.1 Weight to Container (TEU) Conversion
FAF5 reports tonnage in **thousands of short tons**. A TEU-equivalent scenario scale may be constructed as follows:
1. Metric conversion: $1\text{ short ton} = 2,000\text{ lbs} \approx 0.907185\text{ metric tons}$.
2. Select a declared payload assumption and containerization fraction. The working value of **11.5 short tons per TEU** is a modeling assumption, not an estimate contained in FAF5.
3. Compute a TEU equivalent:
   $$\text{Annual TEU} = \frac{\text{Tonnage (in thousands)} \times 1,000}{\text{assumed short tons per TEU}}$$

### 4.2 Disaggregation to Focal-Shipper Demand Scale
FAF represents macroeconomic aggregate regional flows across all shippers and carriers. To calibrate the focal-shipper daily demand $\bar{d}_t$:
$$\bar{d}_t = \frac{\text{Annual TEU}}{365} \times \theta \times \chi \times \sigma$$
where:
* $\theta \in (0, 1]$ is the share of commodity flow moving in intact 40-foot containers;
* $\chi \in (0, 1]$ is the share directed to the focal market distribution centers;
* $\sigma \ll 1$ is the focal shipper's market share (e.g., $0.005$ to $0.02$ for a medium-to-large retail/electronics importer).

### 4.3 Methodological Boundaries
* **Not Firm-Level Orders:** FAF annual estimates reflect multi-source macroeconomic models (CFS, foreign trade Census data, Transsearch). They do not represent daily carrier booking records or order manifests.
* **Not Operating Capacities:** Reported tonnages reflect realized historical equilibrium flows, not the physical or contractual capacity ceilings of rail mainlines, highway lanes, or container lift cranes.
* **Mode-5 Boundary:** `Multiple modes & mail` is not an observed truck--rail intermodal category and must not be used as an intermodal rail market share.
* **Gateway Boundary:** For imports, domestic origin `061` identifies the Los Angeles FAF zone of entry, not a specific seaport. The supplied extract omits `fr_inmode`, so it cannot isolate waterborne imports through POLA/POLB.
* **Coverage Boundary:** The supplied CSV contains 28 of the 72 combinations implied by two destinations, two trade types, three domestic modes, and six commodities. Its mode/trade percentages describe the supplied rows only, not the complete corridor.
* **Provenance Boundary:** The local validation script verifies schema, arithmetic, checksum, and coverage. The 28 row values have not yet been independently reproduced from an uploaded official FAF archive or a saved DTT query.
* **Independent Flow Calibration:** FAF flows provide an inland macroeconomic scale check that is complementary to, but must not be double-counted with, the POLA maritime gateway container volume series.
