import pytest

from audit.services import record_event


@pytest.mark.django_db
def test_record_event_persists_occurrence_audit(admin_user, open_occurrence):
    entry = record_event(
        actor=admin_user,
        action_type="session_opened",
        target_type="session_occurrence",
        target_id=open_occurrence.pk,
        occurrence=open_occurrence,
        metadata={"status": "open"},
    )
    assert entry.occurrence == open_occurrence
    assert entry.actor_user == admin_user
    assert entry.metadata_snapshot["status"] == "open"
