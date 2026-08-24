"""Pinned, validated inputs shared by every chart build."""

from __future__ import annotations

import csv
import hashlib
import io
import urllib.request
from decimal import Decimal

FIVETHIRTYEIGHT_COMMIT = "e0c8091a3ba3be547b15a704b1ceb25b211e676b"
FIVETHIRTYEIGHT_URL = (
    "https://raw.githubusercontent.com/fivethirtyeight/data/"
    f"{FIVETHIRTYEIGHT_COMMIT}/sports-political-donations/"
    "sports-political-donations.csv"
)
FIVETHIRTYEIGHT_SHA256 = "d6602d20049b8d36a1b455135bc4fc5900a2327dbe0f46d7633e2aad3222aca0"
EXPECTED_ROWS = 2_798
EXPECTED_OWNERS = 158
EXPECTED_TOTAL = Decimal("46978697")
EXPECTED_YEARS = [2016, 2018, 2020]

# The Guardian reported at least $132.1M in total and published the other
# dollar figures below. Calculations using the rounded total are approximate.
GUARDIAN_TOTAL_APPROX = 132_100_000
GUARDIAN_REPUBLICAN = 124_806_435
GUARDIAN_DEMOCRATIC = 5_215_693
GUARDIAN_ADELSON = 92_275_100


def fetch_fivethirtyeight_csv() -> bytes:
    request = urllib.request.Request(
        FIVETHIRTYEIGHT_URL,
        headers={"User-Agent": "sports-owner-donations/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != FIVETHIRTYEIGHT_SHA256:
        raise RuntimeError(
            "FiveThirtyEight source checksum mismatch: "
            f"expected {FIVETHIRTYEIGHT_SHA256}, received {actual}"
        )
    return payload


def validate_fivethirtyeight_csv(payload: bytes) -> dict[str, object]:
    rows = list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))))
    required = {"Owner", "Team", "League", "Recipient", "Amount", "Election Year", "Party"}
    if not rows or not required.issubset(rows[0]):
        raise RuntimeError("FiveThirtyEight source schema is incomplete")

    total = sum(
        (
            Decimal(row["Amount"].replace("$", "").replace(",", "").strip())
            for row in rows
        ),
        Decimal(0),
    )
    owners = len({row["Owner"] for row in rows})
    years = sorted({int(row["Election Year"]) for row in rows})
    checks = {
        "row count": (len(rows), EXPECTED_ROWS),
        "owner count": (owners, EXPECTED_OWNERS),
        "dollar total": (total, EXPECTED_TOTAL),
        "election years": (years, EXPECTED_YEARS),
    }
    failures = [f"{label}: expected {expected}, received {actual}" for label, (actual, expected) in checks.items() if actual != expected]
    if failures:
        raise RuntimeError("FiveThirtyEight source validation failed: " + "; ".join(failures))
    return {
        "rows": len(rows),
        "owners": owners,
        "total": total,
        "years": years,
        "sha256": FIVETHIRTYEIGHT_SHA256,
    }


def load_fivethirtyeight_dataframe():
    import pandas as pd

    payload = fetch_fivethirtyeight_csv()
    validate_fivethirtyeight_csv(payload)
    frame = pd.read_csv(io.BytesIO(payload))
    frame["amt"] = (
        frame["Amount"].astype(str).str.replace(r"[$,\s]", "", regex=True).astype(float)
    )
    return frame
