from django.core.management.base import BaseCommand

from sessions.services import process_slot_coverage_deadlines


class Command(BaseCommand):
    help = "Process J-7 reminders and J-2 auto-cancellations for uncovered session slots."

    def handle(self, *args, **options):
        summary = process_slot_coverage_deadlines()
        self.stdout.write(
            self.style.SUCCESS(
                "Processed slot coverage deadlines: "
                f"{summary['reminders_sent']} reminder recipients, "
                f"{summary['slots_auto_cancelled']} slots auto-cancelled, "
                f"{summary['cancellation_notices_sent']} cancellation recipients."
            )
        )
