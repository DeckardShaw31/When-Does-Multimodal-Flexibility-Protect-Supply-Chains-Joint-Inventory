# FAF5.7.1 Data Tabulation Tool (DTT) Query Guide & Official Archive Specification

**Prepared:** October 5, 2026  
**Purpose:** Provide the exact query filter parameters for the online FAF5 Data Tabulation Tool (DTT) and the official Oak Ridge National Laboratory (ORNL) archive specifications to obtain row-level provenance for the Los Angeles–Chicago corridor.

---

## 1. Official National Archive Specification (Option A: Direct Archive Upload)

If obtaining the raw, unabridged nationwide database directly from the official repository host:

| Attribute | Specification |
|---|---|
| **Host Agency** | Oak Ridge National Laboratory (ORNL) Center for Transportation Analysis on behalf of FHWA & BTS |
| **Archive Name** | `FAF5.7.1_2018-2024.zip` |
| **Direct Download URL** | `https://faf.ornl.gov/faf5/data/download_files/FAF5.7.1_2018-2024.zip` |
| **Base Year (2017) URL**| `https://faf.ornl.gov/faf5/data/download_files/FAF5.7.1.zip` |
| **Compressed Size** | ~184 MB (`FAF5.7.1_2018-2024.zip`) / ~45 MB (`FAF5.7.1.zip`) |
| **Uncompressed File** | `FAF5.7.1_2018-2024.csv` (~1.4 GB, ~2.5 million rows) |
| **Target Storage Path** | Place the downloaded ZIP or CSV into `data/raw/` or `data/public/` |

### Reproducible Extraction of LA–Chicago Corridor Rows from National CSV

To extract all Los Angeles–Chicago records from the unzipped 1.4 GB national CSV without loading the entire dataset into memory:

```python
import pandas as pd

# Stream through the official national CSV and filter for Los Angeles (061) -> Chicago (171, 181)
chunk_size = 100_000
chunks = []

for chunk in pd.read_csv("FAF5.7.1_2018-2024.csv", dtype={"dms_orig": str, "dms_dest": str}, chunksize=chunk_size):
    filtered = chunk[(chunk["dms_orig"] == "061") & (chunk["dms_dest"].isin(["171", "181"]))]
    if not filtered.empty:
        chunks.append(filtered)

la_chicago_df = pd.concat(chunks, ignore_index=True)
la_chicago_df.to_csv("faf5_lac_official_all_modes_commodities.csv", index=False)
```

---

## 2. Exact Online DTT Query Configuration (Option B: Web Query Export)

The official interactive web interface is hosted by ORNL at:
**Portal URL:** `https://faf.ornl.gov/faf5/dtt_total.aspx`

Follow this exact parameter sequence to export the Los Angeles to Chicago corridor flows:

### Step 1: Flow Type and Measure Selection
* **Flow Type (`DropDownList_Flow_Type`):** Select `Total Flows` (or run separate queries for `Domestic Flows` and `Import Flows`).
* **Measures (`Select_measure`):** Multi-select:
  1. `Tons (Thousands of Short Tons)`
  2. `Value (Millions of Current Dollars)`
  3. `Ton-Miles (Millions)`
* **Years (`Select_year`):** Select `2024` (or select all years `2017`, `2018`, `2019`, `2020`, `2021`, `2022`, `2023`, `2024`).

### Step 2: Geographic Scope
* **Origin Geography Level (`DropDownList_geo_level_o`):** Select `FAF Zone`.
* **Origin Zone (`Select_o`):**
  * `061` - `Los Angeles-Long Beach-Anaheim, CA`
* **Destination Geography Level (`DropDownList_geo_level_d`):** Select `FAF Zone`.
* **Destination Zones (`Select_d`):** Select both:
  * `171` - `Chicago-Naperville, IL-IN-WI (IL Part)`
  * `181` - `Chicago-Naperville, IL-IN-WI (IN Part)`

### Step 3: Commodity and Mode Filters (Scope Definition)
* **Commodity Selection (`Select_c`):**
  * For the 6 target container-compatible commodities, select:
    * `24` - Plastics and rubber
    * `30` - Textiles, leather, and articles of textiles
    * `35` - Electronic and other electrical equipment
    * `39` - Furniture, mattresses, lamps
    * `40` - Miscellaneous manufactured products
    * `43` - Mixed freight
  * *(Recommendation for true corridor modal shares: Select `All Commodities` to export the full commodity spectrum, allowing an accurate total denominator).*
* **Mode Selection (`Select_m`):**
  * Select the primary land transport modes:
    * `1` - Truck
    * `2` - Rail
    * `5` - Multiple modes & mail
  * *(Recommendation for true corridor modal shares: Select `All Modes` so that Air, Water, and Other are captured, avoiding composition distortion).*

### Step 4: Execution & Download
1. Click the **Run** button (`ContentPlaceHolder1_Button_Run`).
2. Wait for the ASP.NET postback to render the cross-tabulated results panel.
3. Click the **Download CSV** link (`ContentPlaceHolder1_LinkButton_Download`).
4. Save the downloaded file as `faf5_dtt_lac_export.csv`.

---

## 3. Methodological Clarifications on Data Interpretation

### 3.1 The 28 vs. 72 Combinations and Sparse Data Representation
* **Declared Scope:** 2 destination zones (`171`, `181`) $\times$ 2 trade types (`1`, `2`) $\times$ 3 modes (`1`, `2`, `5`) $\times$ 6 commodities (`24`, `30`, `35`, `39`, `40`, `43`) = **72 potential combinations**.
* **Why the initial file had 28 rows:** In nationwide macroeconomic databases (like CFS and FAF), long-distance lane matrices are sparse. Many combinations have zero observed sample flows or fail statistical disclosure thresholds (e.g., domestic carload rail of textiles into northwest Indiana `181`). The initial extract included only the 28 non-zero, dominant flow records.
* **Impact on Metrics:** Summing only those 28 rows produced $4,463.45$ thousand tons. The resulting percentages ($68.2\%$ Mode 5, $26.6\%$ Truck, $5.2\%$ Rail) reflect the **internal composition of those 28 supplied rows**, not the true corridor-wide modal share. 
* **Correction for Manuscript:** When reporting modal shares in `main.tex`, use the full corridor total (including all commodities and all modes) from the raw FAF database or DTT query output as the denominator.

### 3.2 Definition of Mode 5 ("Multiple Modes & Mail")
* **Official BTS/FAF Definition:** Code 5 is titled **"Multiple Modes and Mail"**.
* **What it contains:** Shipments that moved by more than one mode (e.g., truck-rail, truck-air, truck-water) as well as postal and courier shipments (USPS, FedEx, UPS).
* **Operational Boundary in Model:** While intermodal container-on-flatcar (COFC) traffic over the BNSF Southern Transcon and UP corridors represents the bulk of long-haul transcontinental tonnage in this category, Mode 5 is **not** an exclusively pure intermodal-rail observation. In the manuscript, it must be referred to by its official title, with explicit documentation of any assumed intermodal container fraction.
