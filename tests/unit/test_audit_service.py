import pytest

from audit.services import record_event


@pytest.mark.django_db
def test_record_event_persists_slot_audit(admin_user, open_occurrence, open_slot):
    entry = record_event(
        actor=admin_user,
        action_type="slot_updated",
        target_type="session_slot",
        target_id=open_slot.pk,
        occurrence=open_occurrence,
        slot=open_slot,
        metadata={"status": "open"},
    )
    assert entry.occurrence == open_occurrence
    assert entry.slot == open_slot
    assert entry.actor_user == admin_user
    assert entry.metadata_snapshot["status"] == "open"
