"""Validate immutable source contracts without charting dependencies."""

from data_sources import fetch_fivethirtyeight_csv, validate_fivethirtyeight_csv


stats = validate_fivethirtyeight_csv(fetch_fivethirtyeight_csv())
print(
    "Source validation passed: "
    f"{stats['rows']:,} rows, {stats['owners']} owners, "
    f"${stats['total']:,.0f}, sha256 {stats['sha256']}"
)
