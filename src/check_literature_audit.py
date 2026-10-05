import csv
import hashlib
import json
import re
from pathlib import Path

from pypdf import PdfReader


CURRENT_DATE = "2026-10-04"
AUDIT_PATH = Path("literature_audit.csv")
PAPERS_DIRECTORY = Path("papers")
OUTPUT_PATH = Path("results/literature_audit_evidence.json")

EXPECTED = {
    "chen2012": {
        "file": "chen2012.pdf",
        "title": "Resilience: An Indicator of Recovery Capability in Intermodal Freight Transport",
        "markers": ["multivariate correlated random variates", "reserve capacity"],
    },
    "aldrighetti2023": {
        "file": "1-s2.0-S0305048323000075-main.pdf",
        "title": "Efficient resilience portfolio design in the supply chain with consideration of preparedness and recovery investments",
        "markers": ["backup contract", "contracted capacity"],
    },
    "goodarzi2025": {
        "file": "An-optimization-approach-for-resilient-and-sustainable-planni.pdf",
        "title": "An optimization approach for resilient and sustainable planning of intermodal transport",
        "markers": ["first-stage variables", "flood may affect several nodes"],
    },
    "guo2024": {
        "file": "1-s2.0-S0305054824001485-main.pdf",
        "title": "Collaborative optimization of routing and storage strategy of multi-period multimodal transport in an uncertain environment",
        "markers": ["storage strategy", "robust optimization"],
    },
    "rahiminia2025": {
        "file": "1-s2.0-S003801212400346X-main.pdf",
        "title": "A hybrid optimization approach for designing sustainable intermodal freight transport under mixed uncertainty",
        "markers": ["buffer inventory", "capacity of terminals", "storing capacity"],
    },
    "wang2026": {
        "file": "1-s2.0-S1366554526001146-main.pdf",
        "title": "Service pricing in resilient multimodal transportation networks",
        "markers": ["reserve capacity in advance", "rented capacity"],
    },
}


def normalize(text):
    return re.sub(r"\s+", " ", text.casefold()).strip()


def main():
    with AUDIT_PATH.open(newline="") as handle:
        rows = {row["reference_key"]: row for row in csv.DictReader(handle)}
    evidence = {
        "checked_date": CURRENT_DATE,
        "scope": (
            "Verifies uploaded file identity and presence of selected supporting text markers. "
            "Interpretive absence claims remain manual full-text judgments."
        ),
        "papers": {},
    }
    for reference_key, expectation in EXPECTED.items():
        if reference_key not in rows:
            raise ValueError(f"Missing audit row: {reference_key}")
        row = rows[reference_key]
        if row["evidence_level"] != "full_text_audited":
            raise ValueError(f"Unexpected evidence level for {reference_key}")
        if row["local_pdf_status"] != expectation["file"]:
            raise ValueError(f"Audit filename mismatch for {reference_key}")
        path = PAPERS_DIRECTORY / expectation["file"]
        if not path.exists():
            raise FileNotFoundError(path)
        reader = PdfReader(path)
        title = (reader.metadata or {}).get("/Title", "")
        if normalize(expectation["title"]) not in normalize(title):
            raise ValueError(f"Unexpected PDF title for {reference_key}: {title}")
        page_text = [normalize(page.extract_text() or "") for page in reader.pages]
        marker_pages = {}
        for marker in expectation["markers"]:
            pages = [index + 1 for index, text in enumerate(page_text) if normalize(marker) in text]
            if not pages:
                raise ValueError(f"Supporting marker not found for {reference_key}: {marker}")
            marker_pages[marker] = pages
        evidence["papers"][reference_key] = {
            "filename": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "page_count": len(reader.pages),
            "pdf_title": title,
            "supporting_marker_pages": marker_pages,
        }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"Verified {len(EXPECTED)} uploaded PDFs against the audit register.")


if __name__ == "__main__":
    main()