# papier-analyse-classic

Backend + Streamlit prototype for paper load inspections.

## Inspection dashboard API

A new modular dashboard aggregation layer is available for future web/mobile clients.

### Endpoint

`GET /dashboard/inspections`

Serves a dashboard-ready list of inspections ordered by newest first.

### Response fields (per inspection)

- `inspection_id`
- `license_plate`
- `created_timestamp`
- `video_uploaded`
- `frame_count`
- `representative_frame_count`
- `newspaper_score_total`
- `cardboard_score_total`
- `mixed_score_total`
- `decision_recommendation`
- `final_human_decision`
- `recommendation_match_status`

### Optional query parameters

- `limit`
- `offset`
- `decision_recommendation`
- `recommendation_match_status`

### Run API

```bash
uvicorn backend.dashboard_api:app --reload
```

Optional environment variable:

- `INSPECTION_DB_PATH` (defaults to `inspections.db`)

The endpoint is intentionally backend-only and acts as the foundation for a future PWA or mobile inspection dashboard.
