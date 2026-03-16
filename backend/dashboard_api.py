"""HTTP API entry point for inspection dashboard aggregation."""

from __future__ import annotations

import logging
import os
import sqlite3

from fastapi import FastAPI, Query

from backend.inspection_dashboard_service import InspectionDashboardService


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("dashboard-api")

app = FastAPI(title="Inspection Dashboard API", version="0.1.0")


@app.get("/dashboard/inspections")
def get_dashboard_inspections(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    decision_recommendation: str | None = Query(default=None),
    recommendation_match_status: str | None = Query(default=None),
) -> list[dict]:
    """Return dashboard rows ordered by newest inspection."""

    db_path = os.getenv("INSPECTION_DB_PATH", "inspections.db")
    logger.info(
        "dashboard query: limit=%s offset=%s decision_recommendation=%s recommendation_match_status=%s",
        limit,
        offset,
        decision_recommendation,
        recommendation_match_status,
    )

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        service = InspectionDashboardService(connection)
        results = service.list_inspections(
            limit=limit,
            offset=offset,
            decision_recommendation=decision_recommendation,
            recommendation_match_status=recommendation_match_status,
        )

    logger.info("dashboard query returned inspections=%s", len(results))
    return results
