import csv
import io
from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from audit.services import record_event
from sessions.models import CourseEnrollment, SessionSeries

from .identity import TEMPORARY_ACCESS_CODE, build_login_key_from_full_name, build_lookup_key


@dataclass(slots=True)
class BulkImportResult:
    created_count: int = 0
    updated_count: int = 0


def _value_from_row(row: list[str], columns: dict[str, int], key: str) -> str:
    index = columns.get(key)
    if index is None or index >= len(row):
        return ""
    return row[index].strip()


def _is_yes(value: str | None) -> bool:
    return build_lookup_key(value) in {"oui", "yes", "true", "1", "x"}


def _sync_course_enrollments(*, actor, user, target_series_ids: set[int]) -> None:
    previous_course_ids = set(
        CourseEnrollment.objects.active().filter(user=user).values_list("series_id", flat=True)
    )

    for series_id in sorted(target_series_ids - previous_course_ids):
        enrollment = CourseEnrollment.objects.create(
            user=user,
            series_id=series_id,
            assigned_by=actor,
        )
        record_event(
            actor=actor,
            action_type="course_enrollment_assigned",
            target_type="course_enrollment",
            target_id=enrollment.pk,
            metadata={"user_id": user.pk, "series_id": series_id},
        )

    if previous_course_ids - target_series_ids:
        enrollments = CourseEnrollment.objects.active().filter(
            user=user,
            series_id__in=previous_course_ids - target_series_ids,
        )
        for enrollment in enrollments:
            enrollment.status = CourseEnrollment.Status.REMOVED
            enrollment.removed_at = timezone.now()
            enrollment.removed_by = actor
            enrollment.save(update_fields=["status", "removed_at", "removed_by"])
            record_event(
                actor=actor,
                action_type="course_enrollment_removed",
                target_type="course_enrollment",
                target_id=enrollment.pk,
                metadata={"user_id": user.pk, "series_id": enrollment.series_id},
            )


def import_accounts_from_roster(*, actor, roster_data: str) -> BulkImportResult:
    if not roster_data.strip():
        raise ValidationError("Collez le tableau des adhérents avant de lancer l'import.")

    reader = list(csv.reader(io.StringIO(roster_data), delimiter="\t"))
    if not reader:
        raise ValidationError("Le tableau collé est vide.")

    header = {
        build_lookup_key(column_name): index
        for index, column_name in enumerate(reader[0])
    }
    if not {"prenom", "nom"}.issubset(header):
        raise ValidationError("Les colonnes Prénom et Nom sont obligatoires pour l'import.")

    course_series_lookup = {
        build_lookup_key(series.label): series
        for series in SessionSeries.objects.filter(session_type=SessionSeries.SessionType.COURSE)
    }
    UserModel = get_user_model()
    existing_users = {user.login_key: user for user in UserModel.objects.all()}
    parsed_rows: list[dict] = []
    seen_login_keys: set[str] = set()
    errors: list[str] = []

    for line_number, row in enumerate(reader[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue

        first_name = _value_from_row(row, header, "prenom")
        last_name = _value_from_row(row, header, "nom")
        if not first_name or not last_name:
            errors.append(f"Ligne {line_number}: prénom et nom sont obligatoires.")
            continue

        full_name = f"{first_name} {last_name}".strip()
        login_key = build_login_key_from_full_name(full_name)
        if login_key in seen_login_keys:
            errors.append(f"Ligne {line_number}: doublon détecté pour {full_name}.")
            continue
        seen_login_keys.add(login_key)

        series_label = _value_from_row(row, header, "creneau")
        series = None
        if series_label:
            series = course_series_lookup.get(build_lookup_key(series_label))
            if series is None:
                errors.append(f"Ligne {line_number}: créneau inconnu \"{series_label}\".")
                continue

        comment = _value_from_row(row, header, "commentaire")
        wants_orange_passport = _is_yes(_value_from_row(row, header, "passeportorange")) or (
            build_lookup_key(comment) in {"passeportorange", "securiteorange"}
        )
        wants_responsable = _is_yes(_value_from_row(row, header, "referentsalle"))
        parsed_rows.append(
            {
                "full_name": full_name,
                "login_key": login_key,
                "series_ids": {series.pk} if series is not None else set(),
                "wants_orange_passport": wants_orange_passport,
                "wants_responsable": wants_responsable,
            }
        )

    if errors:
        raise ValidationError(errors)

    result = BulkImportResult()
    with transaction.atomic():
        for item in parsed_rows:
            user = existing_users.get(item["login_key"])
            created = user is None
            if created:
                user = UserModel.objects.create_user(
                    email=None,
                    password=TEMPORARY_ACCESS_CODE,
                    full_name=item["full_name"],
                    role=UserModel.Role.MEMBER,
                    is_active=True,
                    password_state=UserModel.PasswordState.TEMPORARY,
                )
            else:
                if user.is_admin_role:
                    raise ValidationError(f"Le compte admin {user.full_name} ne peut pas être modifié par l'import.")
                user.full_name = item["full_name"]
                user.role = UserModel.Role.MEMBER
                user.is_active = True

            if item["wants_responsable"] and not user.is_responsable_accredited:
                user.grant_responsable_accreditation(actor=actor)
            elif not item["wants_responsable"] and user.is_responsable_accredited:
                user.revoke_responsable_accreditation()

            if item["wants_orange_passport"] and not user.has_orange_passport:
                user.grant_orange_passport(actor=actor)
            elif not item["wants_orange_passport"] and user.has_orange_passport:
                user.revoke_orange_passport()

            user.save()
            _sync_course_enrollments(actor=actor, user=user, target_series_ids=item["series_ids"])

            if created:
                result.created_count += 1
                record_event(
                    actor=actor,
                    action_type="account_created",
                    target_type="account",
                    target_id=user.pk,
                    reason="bulk roster import",
                    metadata={
                        "role": user.role,
                        "is_responsable_accredited": user.is_responsable_accredited,
                        "has_orange_passport": user.has_orange_passport,
                        "course_series_ids": sorted(item["series_ids"]),
                        "password_state": user.password_state,
                    },
                )
            else:
                result.updated_count += 1
                record_event(
                    actor=actor,
                    action_type="account_updated",
                    target_type="account",
                    target_id=user.pk,
                    reason="bulk roster import",
                    metadata={
                        "is_active": user.is_active,
                        "role": user.role,
                        "is_responsable_accredited": user.is_responsable_accredited,
                        "has_orange_passport": user.has_orange_passport,
                        "course_series_ids": sorted(item["series_ids"]),
                    },
                )

    return result
