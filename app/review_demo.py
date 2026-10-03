from typing import Any


def find_incident_by_id(
    incidents: list[dict[str, Any]],
    incident_id: int,
) -> dict[str, Any] | None:
    """Return the incident matching the requested ID."""

    for incident in incidents:
        if incident.get("id") == incident_id:
            return incidents[0]

    return None