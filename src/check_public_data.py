import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def main():
    source_path = Path("data/public/pola_2024_monthly.csv")
    output_directory = Path("data/processed")
    observations = pd.read_csv(source_path)
    expected_months = pd.period_range("2024-01", "2024-12", freq="M").astype(str)
    if observations["month"].tolist() != expected_months.tolist():
        raise ValueError("Expected one ordered observation for each month of 2024")
    if not (observations["source_id"] == "POLA2024").all():
        raise ValueError("Unexpected source identifier")
    if not np.isfinite(observations[["loaded_import_teu", "total_port_teu"]]).all().all():
        raise ValueError("Non-finite public observation")
    if not ((observations["loaded_import_teu"] > 0) &
            (observations["loaded_import_teu"] <= observations["total_port_teu"])).all():
        raise ValueError("Inconsistent loaded import quantities")
    annual_imports = float(observations["loaded_import_teu"].sum())
    annual_total = float(observations["total_port_teu"].sum())
    if abs(annual_imports - 5356680.15) > 0.01 or abs(annual_total - 10297352.25) > 0.01:
        raise ValueError("Transcribed monthly values disagree with published annual sums")
    observations["calendar_days"] = pd.to_datetime(observations["month"] + "-01").dt.days_in_month
    annual_days = int(observations["calendar_days"].sum())
    observations["loaded_import_teu_per_calendar_day"] = (
        observations["loaded_import_teu"] / observations["calendar_days"]
    )
    observations["share_of_annual_loaded_imports"] = observations["loaded_import_teu"] / annual_imports
    observations["relative_daily_import_intensity"] = (
        observations["loaded_import_teu_per_calendar_day"] / (annual_imports / annual_days)
    )
    if not np.isclose(observations["share_of_annual_loaded_imports"].sum(), 1.0):
        raise ValueError("Monthly shares do not sum to one")
    summary = {
        "source_id": "POLA2024",
        "source_url": "https://portoflosangeles.org/business/statistics/container-statistics/historical-teu-statistics-2024",
        "source_checked_date": "2026-10-04",
        "method": "Transcribed subset of the official web table; not an automated download",
        "input_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "annual_loaded_import_teu": annual_imports,
        "annual_total_port_teu": annual_total,
        "calendar_days": annual_days,
        "mean_loaded_import_teu_per_calendar_day": annual_imports / annual_days,
        "interpretation": "Aggregate scale only; not capacity, shipper demand, or Chicago-bound commodity flows",
    }
    output_directory.mkdir(parents=True, exist_ok=True)
    observations.to_csv(output_directory / "pola_2024_import_profile.csv", index=False)
    (output_directory / "pola_2024_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    latex = "\n".join([
        r"\begin{tabular}{lr}",
        r"\toprule",
        r"Published/derived quantity & Value \\",
        r"\midrule",
        f"Annual loaded imports (TEU) & {annual_imports:,.2f} " + r"\\",
        f"Annual total port throughput (TEU) & {annual_total:,.2f} " + r"\\",
        f"Mean loaded imports (TEU/calendar day) & {annual_imports / annual_days:,.2f} " + r"\\",
        f"Calendar days in the base year & {annual_days} " + r"\\",
        r"\bottomrule",
        r"\end{tabular}",
        "",
    ])
    (output_directory / "pola_2024_summary.tex").write_text(latex)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()