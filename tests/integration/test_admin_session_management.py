import datetime as dt

import pytest
from django.urls import reverse
from django.utils import timezone

from bookings.models import Reservation
from bookings.services import create_member_booking
from sessions.models import SessionOccurrence, SessionSeries, SessionSlot
from sessions import services as session_services
from sessions.services import assign_slot_responsibility


@pytest.mark.django_db
def test_admin_can_create_series_and_occurrence(client, admin_user):
    client.force_login(admin_user)
    landing = client.get(reverse("sessions_admin:series-list"))
    assert landing.status_code == 200
    landing_html = landing.content.decode()
    assert "Pilotage des séances" in landing_html
    assert "Administration" in landing_html

    response = client.post(
        reverse("sessions_admin:series-create"),
        {
            "label": "Mercredi libre",
            "weekday": SessionSeries.Weekday.WEDNESDAY,
            "start_time": "19:00",
            "end_time": "21:00",
            "default_capacity": 16,
            "is_active": "on",
            "slot_templates-TOTAL_FORMS": "0",
            "slot_templates-INITIAL_FORMS": "0",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert "Série créée." in response.content.decode()
    assert SessionSeries.objects.filter(label="Mercredi libre").exists()
    assert SessionOccurrence.objects.filter(series__label="Mercredi libre").exists()


@pytest.mark.django_db
def test_admin_can_create_one_off_occurrence_with_slot_generation(client, admin_user):
    client.force_login(admin_user)
    create_page = client.get(reverse("sessions_admin:occurrence-create"))
    assert create_page.status_code == 200
    assert "Mettre à jour le statut de la séance" not in create_page.content.decode()

    response = client.post(
        reverse("sessions_admin:occurrence-create"),
        {
            "label": "Weekend libre",
            "session_date": (dt.date.today() + dt.timedelta(days=10)).isoformat(),
            "start_time": "10:00",
            "end_time": "13:00",
            "capacity": 30,
            "status": SessionOccurrence.Status.OPEN,
            "notes": "",
        },
        follow=True,
    )
    assert response.status_code == 200
    occurrence = SessionOccurrence.objects.get(label="Weekend libre")
    assert occurrence.slots.count() == 2
    assert "Séance créée." in response.content.decode()


@pytest.mark.django_db
def test_admin_can_change_occurrence_status(client, admin_user, open_occurrence):
    client.force_login(admin_user)
    edit_page = client.get(reverse("sessions_admin:occurrence-edit", args=[open_occurrence.pk]))
    assert edit_page.status_code == 200
    edit_html = edit_page.content.decode()
    assert "Mettre à jour le statut de la séance" in edit_html
    assert "Découpage et couverture" in edit_html

    response = client.post(
        reverse("sessions_admin:occurrence-status", args=[open_occurrence.pk]),
        {"status": SessionOccurrence.Status.CLOSED, "reason": "Salle pleine"},
        follow=True,
    )
    assert response.status_code == 200
    open_occurrence.refresh_from_db()
    assert open_occurrence.status == SessionOccurrence.Status.CLOSED


@pytest.mark.django_db
def test_admin_series_list_only_shows_upcoming_occurrences(client, admin_user, monkeypatch):
    client.force_login(admin_user)
    fixed_now = timezone.make_aware(dt.datetime(2026, 3, 10, 15, 0))
    monkeypatch.setattr(session_services.timezone, "localdate", lambda: fixed_now.date())
    monkeypatch.setattr(session_services.timezone, "localtime", lambda *args, **kwargs: fixed_now)

    SessionOccurrence.objects.bulk_create(
        [
            SessionOccurrence(
                label="Seance passee",
                session_date=dt.date(2026, 3, 9),
                start_time=dt.time(18, 0),
                end_time=dt.time(20, 0),
                capacity=12,
                session_type=SessionSeries.SessionType.FREE_PRACTICE,
                status=SessionOccurrence.Status.OPEN,
                created_by=admin_user,
            ),
            SessionOccurrence(
                label="Seance du jour terminee",
                session_date=dt.date(2026, 3, 10),
                start_time=dt.time(13, 0),
                end_time=dt.time(14, 0),
                capacity=12,
                session_type=SessionSeries.SessionType.FREE_PRACTICE,
                status=SessionOccurrence.Status.OPEN,
                created_by=admin_user,
            ),
            SessionOccurrence(
                label="Seance du jour encore ouverte",
                session_date=dt.date(2026, 3, 10),
                start_time=dt.time(16, 0),
                end_time=dt.time(17, 0),
                capacity=12,
                session_type=SessionSeries.SessionType.FREE_PRACTICE,
                status=SessionOccurrence.Status.OPEN,
                created_by=admin_user,
            ),
            SessionOccurrence(
                label="Seance future",
                session_date=dt.date(2026, 3, 11),
                start_time=dt.time(10, 0),
                end_time=dt.time(12, 0),
                capacity=12,
                session_type=SessionSeries.SessionType.FREE_PRACTICE,
                status=SessionOccurrence.Status.OPEN,
                created_by=admin_user,
            ),
            SessionOccurrence(
                label="Seance future annulee",
                session_date=dt.date(2026, 3, 12),
                start_time=dt.time(10, 0),
                end_time=dt.time(12, 0),
                capacity=12,
                session_type=SessionSeries.SessionType.FREE_PRACTICE,
                status=SessionOccurrence.Status.CANCELLED,
                created_by=admin_user,
            ),
        ]
    )

    response = client.get(reverse("sessions_admin:series-list"))

    assert response.status_code == 200
    html = response.content.decode()
    assert "Seance passee" not in html
    assert "Seance du jour terminee" not in html
    assert "Seance du jour encore ouverte" in html
    assert "Seance future" in html
    assert "Seance future annulee" in html
    assert html.index("Seance du jour encore ouverte") < html.index("Seance future")
    assert html.index("Seance future") < html.index("Seance future annulee")


@pytest.mark.django_db
def test_admin_series_list_shows_upcoming_empty_state(client, admin_user, monkeypatch):
    client.force_login(admin_user)
    fixed_now = timezone.make_aware(dt.datetime(2026, 3, 10, 15, 0))
    monkeypatch.setattr(session_services.timezone, "localdate", lambda: fixed_now.date())
    monkeypatch.setattr(session_services.timezone, "localtime", lambda *args, **kwargs: fixed_now)

    SessionOccurrence.objects.create(
        label="Seance passee",
        session_date=dt.date(2026, 3, 9),
        start_time=dt.time(18, 0),
        end_time=dt.time(20, 0),
        capacity=12,
        session_type=SessionSeries.SessionType.FREE_PRACTICE,
        status=SessionOccurrence.Status.OPEN,
        created_by=admin_user,
    )
    SessionOccurrence.objects.create(
        label="Seance du jour terminee",
        session_date=dt.date(2026, 3, 10),
        start_time=dt.time(13, 0),
        end_time=dt.time(14, 0),
        capacity=12,
        session_type=SessionSeries.SessionType.FREE_PRACTICE,
        status=SessionOccurrence.Status.OPEN,
        created_by=admin_user,
    )

    response = client.get(reverse("sessions_admin:series-list"))

    assert response.status_code == 200
    assert "Aucune occurrence à venir." in response.content.decode()


@pytest.mark.django_db
def test_admin_cannot_modify_past_occurrence_or_past_slot(client, admin_user):
    client.force_login(admin_user)
    past_date = timezone.localdate() - dt.timedelta(days=2)
    occurrence = SessionOccurrence.objects.create(
        label="Seance passee en lecture",
        session_date=past_date,
        start_time=dt.time(18, 0),
        end_time=dt.time(20, 0),
        capacity=12,
        session_type=SessionSeries.SessionType.FREE_PRACTICE,
        status=SessionOccurrence.Status.OPEN,
        created_by=admin_user,
    )
    slot = SessionSlot.objects.create(
        occurrence=occurrence,
        sequence_index=1,
        start_time=dt.time(18, 0),
        end_time=dt.time(19, 30),
        capacity=12,
        status=SessionSlot.Status.OPEN,
    )

    response = client.post(
        reverse("sessions_admin:occurrence-edit", args=[occurrence.pk]),
        {
            "label": "Seance passee modifiee",
            "session_date": occurrence.session_date.isoformat(),
            "start_time": occurrence.start_time.strftime("%H:%M"),
            "end_time": occurrence.end_time.strftime("%H:%M"),
            "capacity": occurrence.capacity,
            "status": occurrence.status,
            "notes": "",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert "Les occurrences passées sont en lecture seule." in response.content.decode()
    occurrence.refresh_from_db()
    assert occurrence.label == "Seance passee en lecture"

    response = client.post(
        reverse("sessions_admin:slot-edit", args=[slot.pk]),
        {
            "start_time": "18:15",
            "end_time": "19:30",
            "capacity": slot.capacity,
            "status": slot.status,
        },
        follow=True,
    )
    assert response.status_code == 200
    assert "Les créneaux passés sont en lecture seule." in response.content.decode()
    slot.refresh_from_db()
    assert slot.start_time == dt.time(18, 0)

    response = client.post(
        reverse("sessions_admin:occurrence-status", args=[occurrence.pk]),
        {"status": SessionOccurrence.Status.CANCELLED, "reason": "test"},
        follow=True,
    )
    assert response.status_code == 200
    assert "Les occurrences passées sont en lecture seule." in response.content.decode()
    occurrence.refresh_from_db()
    assert occurrence.status == SessionOccurrence.Status.OPEN


@pytest.mark.django_db
def test_admin_can_freely_correct_committed_responsable_slot(
    client,
    admin_user,
    member_user,
    member_user_2,
    open_occurrence,
    open_slot,
):
    client.force_login(admin_user)
    assign_slot_responsibility(actor=admin_user, slot=open_slot, user=admin_user)
    Reservation.objects.create(slot=open_slot, user=member_user, created_by_role="admin")
    Reservation.objects.create(slot=open_slot, user=member_user_2, created_by_role="admin")

    response = client.post(
        reverse("sessions_admin:slot-edit", args=[open_slot.pk]),
        {
            "start_time": "18:00",
            "end_time": "22:00",
            "capacity": 1,
            "status": open_slot.status,
        },
        follow=True,
    )

    assert response.status_code == 200
    assert "Créneau mis à jour." in response.content.decode()
    open_slot.refresh_from_db()
    assert open_slot.start_time == dt.time(18, 0)
    assert open_slot.end_time == dt.time(22, 0)
    assert open_slot.capacity == 1
    assert open_slot.current_responsable == admin_user

    response = client.post(
        reverse("sessions_admin:slot-edit", args=[open_slot.pk]),
        {
            "start_time": "20:00",
            "end_time": "19:00",
            "capacity": 1,
            "status": open_slot.status,
        },
        follow=True,
    )

    assert response.status_code == 200
    assert "Créneau mis à jour." in response.content.decode()
    open_slot.refresh_from_db()
    assert open_slot.start_time == dt.time(20, 0)
    assert open_slot.end_time == dt.time(19, 0)


@pytest.mark.django_db
def test_admin_updating_series_realigns_all_occurrences(client, admin_user):
    client.force_login(admin_user)
    series = SessionSeries.objects.create(
        label="Mercredi libre",
        weekday=SessionSeries.Weekday.WEDNESDAY,
        start_time=dt.time(19, 0),
        end_time=dt.time(21, 0),
        default_capacity=16,
        session_type=SessionSeries.SessionType.FREE_PRACTICE,
        created_by=admin_user,
    )
    occurrence_a = SessionOccurrence.objects.create(
        series=series,
        label=series.label,
        session_date=timezone.localdate() + dt.timedelta(days=1),
        start_time=series.start_time,
        end_time=series.end_time,
        capacity=series.default_capacity,
        session_type=series.session_type,
        status=SessionOccurrence.Status.OPEN,
        created_by=admin_user,
    )
    occurrence_b = SessionOccurrence.objects.create(
        series=series,
        label=series.label,
        session_date=timezone.localdate() + dt.timedelta(days=8),
        start_time=series.start_time,
        end_time=series.end_time,
        capacity=series.default_capacity,
        session_type=series.session_type,
        status=SessionOccurrence.Status.OPEN,
        created_by=admin_user,
    )

    response = client.post(
        reverse("sessions_admin:series-edit", args=[series.pk]),
        {
            "label": "Jeudi libre",
            "weekday": SessionSeries.Weekday.THURSDAY,
            "start_time": "20:00",
            "end_time": "22:00",
            "default_capacity": 20,
            "is_active": "on",
            "session_type": SessionSeries.SessionType.FREE_PRACTICE,
            "default_teacher": "",
            "slot_templates-TOTAL_FORMS": "0",
            "slot_templates-INITIAL_FORMS": "0",
        },
        follow=True,
    )

    assert response.status_code == 200
    series.refresh_from_db()
    occurrence_a.refresh_from_db()
    occurrence_b.refresh_from_db()
    expected_dates = []
    for offset in range(2):
        day = timezone.localdate() + dt.timedelta(days=offset * 7)
        expected_dates.append(day + dt.timedelta((SessionSeries.Weekday.THURSDAY - day.weekday()) % 7))

    assert series.label == "Jeudi libre"
    assert occurrence_a.label == "Jeudi libre"
    assert occurrence_b.label == "Jeudi libre"
    assert occurrence_a.session_date == expected_dates[0]
    assert occurrence_b.session_date == expected_dates[1]
    assert occurrence_a.start_time == dt.time(20, 0)
    assert occurrence_b.start_time == dt.time(20, 0)
    assert occurrence_a.capacity == 20
    assert occurrence_b.capacity == 20


@pytest.mark.django_db
def test_admin_updating_series_with_past_occurrences_avoids_unique_date_collision(
    client,
    admin_user,
    monkeypatch,
):
    client.force_login(admin_user)
    fixed_today = dt.date(2026, 4, 11)
    monkeypatch.setattr(session_services.timezone, "localdate", lambda: fixed_today)

    series = SessionSeries.objects.create(
        label="Dimanche libre",
        weekday=SessionSeries.Weekday.SUNDAY,
        start_time=dt.time(19, 0),
        end_time=dt.time(21, 0),
        default_capacity=16,
        session_type=SessionSeries.SessionType.FREE_PRACTICE,
        created_by=admin_user,
    )
    for session_date in [dt.date(2026, 4, 5), dt.date(2026, 4, 12), dt.date(2026, 4, 19)]:
        SessionOccurrence.objects.create(
            series=series,
            label=series.label,
            session_date=session_date,
            start_time=series.start_time,
            end_time=series.end_time,
            capacity=series.default_capacity,
            session_type=series.session_type,
            status=SessionOccurrence.Status.OPEN,
            created_by=admin_user,
        )

    response = client.post(
        reverse("sessions_admin:series-edit", args=[series.pk]),
        {
            "label": "Dimanche libre ajuste",
            "weekday": SessionSeries.Weekday.SUNDAY,
            "start_time": "20:00",
            "end_time": "22:00",
            "default_capacity": 18,
            "is_active": "on",
            "session_type": SessionSeries.SessionType.FREE_PRACTICE,
            "default_teacher": "",
            "slot_templates-TOTAL_FORMS": "0",
            "slot_templates-INITIAL_FORMS": "0",
        },
        follow=True,
    )

    assert response.status_code == 200
    assert "Série mise à jour." in response.content.decode()
    updated_dates = list(
        series.occurrences.order_by("session_date", "id").values_list("session_date", flat=True)
    )
    assert updated_dates == [dt.date(2026, 4, 12), dt.date(2026, 4, 19), dt.date(2026, 4, 26)]


@pytest.mark.django_db
def test_admin_can_delete_occurrence_with_existing_attendee_and_responsable(
    client,
    admin_user,
    member_user,
    open_occurrence,
    open_slot,
):
    client.force_login(admin_user)
    create_member_booking(user=member_user, occurrence=open_occurrence)
    assign_slot_responsibility(actor=admin_user, slot=open_slot, user=admin_user)

    edit_page = client.get(reverse("sessions_admin:occurrence-edit", args=[open_occurrence.pk]))
    assert edit_page.status_code == 200
    html = edit_page.content.decode()
    assert member_user.full_name in html
    assert admin_user.full_name in html
    assert "Cette suppression retirera aussi ces inscriptions et affectations." in html

    response = client.post(
        reverse("sessions_admin:occurrence-delete", args=[open_occurrence.pk]),
        follow=True,
    )

    assert response.status_code == 200
    assert "Séance supprimée." in response.content.decode()
    assert not SessionOccurrence.objects.filter(pk=open_occurrence.pk).exists()
    assert not Reservation.objects.filter(occurrence=open_occurrence).exists()


@pytest.mark.django_db
def test_admin_can_delete_series_with_existing_attendee_and_responsable(
    client,
    admin_user,
    member_user,
    open_occurrence,
    open_slot,
):
    client.force_login(admin_user)
    create_member_booking(user=member_user, occurrence=open_occurrence)
    assign_slot_responsibility(actor=admin_user, slot=open_slot, user=admin_user)
    series = SessionSeries.objects.create(
        label="Mercredi libre",
        weekday=SessionSeries.Weekday.WEDNESDAY,
        start_time=dt.time(19, 0),
        end_time=dt.time(21, 0),
        default_capacity=16,
        session_type=SessionSeries.SessionType.FREE_PRACTICE,
        created_by=admin_user,
    )
    open_occurrence.series = series
    open_occurrence.save(update_fields=["series"])

    edit_page = client.get(reverse("sessions_admin:series-edit", args=[series.pk]))
    assert edit_page.status_code == 200
    html = edit_page.content.decode()
    assert open_occurrence.label in html
    assert "Cette suppression retirera aussi les séances, inscriptions et affectations liées." in html

    response = client.post(
        reverse("sessions_admin:series-delete", args=[series.pk]),
        follow=True,
    )

    assert response.status_code == 200
    assert "Série supprimée." in response.content.decode()
    assert not SessionSeries.objects.filter(pk=series.pk).exists()
    assert not SessionOccurrence.objects.filter(pk=open_occurrence.pk).exists()


@pytest.mark.django_db
def test_series_edit_exposes_and_updates_slot_templates(client, admin_user):
    client.force_login(admin_user)
    series = SessionSeries.objects.create(
        label="Mercredi libre",
        weekday=SessionSeries.Weekday.WEDNESDAY,
        start_time=dt.time(19, 0),
        end_time=dt.time(21, 0),
        default_capacity=16,
        session_type=SessionSeries.SessionType.FREE_PRACTICE,
        created_by=admin_user,
    )

    edit_page = client.get(reverse("sessions_admin:series-edit", args=[series.pk]))
    assert edit_page.status_code == 200
    html = edit_page.content.decode()
    assert "Créneaux par défaut" in html

    response = client.post(
        reverse("sessions_admin:series-edit", args=[series.pk]),
        {
            "label": "Mercredi libre",
            "weekday": SessionSeries.Weekday.WEDNESDAY,
            "start_time": "19:00",
            "end_time": "21:00",
            "default_capacity": 16,
            "session_type": SessionSeries.SessionType.FREE_PRACTICE,
            "is_active": "on",
            "slot_templates-TOTAL_FORMS": "1",
            "slot_templates-INITIAL_FORMS": "0",
            "slot_templates-0-sequence_index": "1",
            "slot_templates-0-start_time": "19:00",
            "slot_templates-0-end_time": "21:00",
        },
        follow=True,
    )

    assert response.status_code == 200
    assert series.slot_templates.count() == 1
    template = series.slot_templates.first()
    assert template.start_time == dt.time(19, 0)
    assert template.end_time == dt.time(21, 0)


@pytest.mark.django_db
def test_admin_can_delete_all_responsable_slots_and_keep_occurrence_without_slots(
    client,
    admin_user,
    open_occurrence,
):
    client.force_login(admin_user)
    slot_ids = list(open_occurrence.slots.order_by("sequence_index").values_list("id", flat=True))

    for slot_id in slot_ids:
        response = client.post(
            reverse("sessions_admin:slot-delete", args=[slot_id]),
            follow=True,
        )
        assert response.status_code == 200

    open_occurrence.refresh_from_db()
    assert open_occurrence.slots.count() == 0

    response = client.post(
        reverse("sessions_admin:occurrence-edit", args=[open_occurrence.pk]),
        {
            "label": open_occurrence.label,
            "session_date": open_occurrence.session_date.isoformat(),
            "start_time": open_occurrence.start_time.strftime("%H:%M"),
            "end_time": open_occurrence.end_time.strftime("%H:%M"),
            "capacity": open_occurrence.capacity,
            "status": open_occurrence.status,
            "notes": "Sans créneau responsable",
        },
        follow=True,
    )

    assert response.status_code == 200
    open_occurrence.refresh_from_db()
    assert open_occurrence.slots.count() == 0
    assert "Aucun créneau généré" in response.content.decode()
