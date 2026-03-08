from django import forms

from .models import EmailAutomationSettings, SessionOccurrence, SessionSeries


class SessionSeriesForm(forms.ModelForm):
    class Meta:
        model = SessionSeries
        fields = ["label", "weekday", "start_time", "end_time", "default_capacity", "is_active"]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }


class SessionOccurrenceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            (SessionOccurrence.Status.OPEN, "Open"),
            (SessionOccurrence.Status.CANCELLED, "Cancelled"),
        ]
        self.fields["status"].initial = SessionOccurrence.Status.OPEN

    class Meta:
        model = SessionOccurrence
        fields = [
            "series",
            "label",
            "session_date",
            "start_time",
            "end_time",
            "capacity",
            "status",
            "notes",
        ]
        widgets = {
            "session_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }


class EmailAutomationSettingsForm(forms.ModelForm):
    class Meta:
        model = EmailAutomationSettings
        fields = [
            "reminder_days_before",
            "cancellation_days_before",
            "reminder_email_subject",
            "reminder_email_body",
            "cancellation_email_subject",
            "cancellation_email_body",
        ]
        widgets = {
            "reminder_days_before": forms.NumberInput(attrs={"min": 1}),
            "cancellation_days_before": forms.NumberInput(attrs={"min": 0}),
            "reminder_email_body": forms.Textarea(attrs={"rows": 8}),
            "cancellation_email_body": forms.Textarea(attrs={"rows": 8}),
        }
