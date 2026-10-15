
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID", "326431794")

OUTPUT_FILE = Path("data/visitors.json")


def main():
    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[
            DateRange(
                start_date="30daysAgo",
                end_date="yesterday",
            )
        ],
        dimensions=[
            Dimension(name="country"),
            Dimension(name="countryId"),
        ],
        metrics=[
            Metric(name="activeUsers"),
        ],
        limit=250,
    )

    response = client.run_report(request)

    countries = []

    for row in response.rows:
        country = row.dimension_values[0].value
        country_code = row.dimension_values[1].value
        visitors = int(row.metric_values[0].value)

        if country_code in ("", "ZZ") or visitors <= 0:
            continue

        countries.append({
            "country": country,
            "countryCode": country_code,
            "visitors": visitors,
        })

    countries.sort(
        key=lambda item: item["visitors"],
        reverse=True,
    )

    result = {
        "source": "Google Analytics 4",
        "propertyId": PROPERTY_ID,
        "metric": "activeUsers",
        "period": "last_30_completed_days",
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "countries": countries,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Updated {OUTPUT_FILE}")
    print(f"Countries returned: {len(countries)}")


if __name__ == "__main__":
    main()
