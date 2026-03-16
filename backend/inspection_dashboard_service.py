"""Inspection dashboard aggregation service.

This module provides a reusable service layer that can be consumed by API
endpoints, background jobs, or future mobile/PWA delivery channels.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any
import sqlite3


@dataclass(slots=True)
class InspectionDashboardItem:
    inspection_id: int
    license_plate: str | None
    created_timestamp: str
    video_uploaded: bool
    frame_count: int
    representative_frame_count: int
    newspaper_score_total: float
    cardboard_score_total: float
    mixed_score_total: float
    decision_recommendation: str | None
    final_human_decision: str | None
    recommendation_match_status: str | None


class InspectionDashboardService:
    """Aggregates inspection data into dashboard-friendly records."""

    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def list_inspections(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        decision_recommendation: str | None = None,
        recommendation_match_status: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return inspection dashboard rows ordered by newest first."""

        # Defensive bounds for pagination.
        limit = max(1, min(limit, 500))
        offset = max(0, offset)

        query = """
        WITH frame_stats AS (
            SELECT
                inspection_id,
                COUNT(*) AS frame_count,
                SUM(CASE WHEN COALESCE(is_representative, 0) = 1 THEN 1 ELSE 0 END) AS representative_frame_count
            FROM frames
            GROUP BY inspection_id
        )
        SELECT
            i.id AS inspection_id,
            i.license_plate,
            i.created_timestamp,
            CASE WHEN COALESCE(v.upload_completed, 0) = 1 THEN 1 ELSE 0 END AS video_uploaded,
            COALESCE(fs.frame_count, 0) AS frame_count,
            COALESCE(fs.representative_frame_count, 0) AS representative_frame_count,
            COALESCE(ms.newspaper_score_total, 0) AS newspaper_score_total,
            COALESCE(ms.cardboard_score_total, 0) AS cardboard_score_total,
            COALESCE(ms.mixed_score_total, 0) AS mixed_score_total,
            r.decision_recommendation,
            hf.final_human_decision,
            hf.recommendation_match_status
        FROM inspections i
        LEFT JOIN videos v ON v.inspection_id = i.id
        LEFT JOIN frame_stats fs ON fs.inspection_id = i.id
        LEFT JOIN material_scores ms ON ms.inspection_id = i.id
        LEFT JOIN recommendations r ON r.inspection_id = i.id
        LEFT JOIN human_feedback hf ON hf.inspection_id = i.id
        WHERE (:decision_recommendation IS NULL OR r.decision_recommendation = :decision_recommendation)
          AND (:recommendation_match_status IS NULL OR hf.recommendation_match_status = :recommendation_match_status)
        ORDER BY i.created_timestamp DESC
        LIMIT :limit OFFSET :offset
        """

        rows = self._connection.execute(
            query,
            {
                "limit": limit,
                "offset": offset,
                "decision_recommendation": decision_recommendation,
                "recommendation_match_status": recommendation_match_status,
            },
        ).fetchall()

        return [
            asdict(
                InspectionDashboardItem(
                    inspection_id=row["inspection_id"],
                    license_plate=row["license_plate"],
                    created_timestamp=row["created_timestamp"],
                    video_uploaded=bool(row["video_uploaded"]),
                    frame_count=row["frame_count"],
                    representative_frame_count=row["representative_frame_count"],
                    newspaper_score_total=row["newspaper_score_total"],
                    cardboard_score_total=row["cardboard_score_total"],
                    mixed_score_total=row["mixed_score_total"],
                    decision_recommendation=row["decision_recommendation"],
                    final_human_decision=row["final_human_decision"],
                    recommendation_match_status=row["recommendation_match_status"],
                )
            )
            for row in rows
        ]
