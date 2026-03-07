import pytest
from django.core.exceptions import ValidationError

from bookings.services import create_member_booking


@pytest.mark.django_db
def test_member_cannot_book_twice(member_user, open_occurrence):
    create_member_booking(user=member_user, occurrence=open_occurrence)
    with pytest.raises(ValidationError):
        create_member_booking(user=member_user, occurrence=open_occurrence)


@pytest.mark.django_db
def test_last_seat_contention_rejected(member_user, member_user_2, open_occurrence):
    open_occurrence.capacity = 1
    open_occurrence.save()

    create_member_booking(user=member_user, occurrence=open_occurrence)

    with pytest.raises(ValidationError):
        create_member_booking(user=member_user_2, occurrence=open_occurrence)
