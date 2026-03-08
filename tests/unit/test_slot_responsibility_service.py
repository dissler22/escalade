import pytest
from django.core.exceptions import ValidationError

from sessions.models import ResponsibleAssignment
from sessions.services import release_slot_responsibility, take_slot_responsibility


@pytest.mark.django_db
def test_responsable_can_take_and_release_slot(responsable_user, open_slot):
    assignment = take_slot_responsibility(user=responsable_user, slot=open_slot)

    assert assignment.slot == open_slot
    assert assignment.user == responsable_user
    assert open_slot.current_responsable == responsable_user

    released = release_slot_responsibility(actor=responsable_user, slot=open_slot)

    assert released.status == ResponsibleAssignment.Status.RELEASED
    assert not open_slot.responsable_assignments.filter(status=ResponsibleAssignment.Status.ACTIVE).exists()


@pytest.mark.django_db
def test_second_responsable_is_rejected(admin_user, responsable_user, open_slot):
    admin_user.grant_responsable_accreditation()
    admin_user.save()
    take_slot_responsibility(user=responsable_user, slot=open_slot)

    with pytest.raises(ValidationError):
        take_slot_responsibility(user=admin_user, slot=open_slot)
