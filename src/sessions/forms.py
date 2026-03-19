from django import forms
from django.contrib.auth import get_user_model

from .models import EmailAutomationSettings, SessionOccurrence, SessionSeries


def _teacher_queryset():
    return get_user_model().objects.filter(is_active=True).order_by("full_name")


class SessionSeriesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["default_teacher"].queryset = _teacher_queryset()
        self.fields["session_type"].required = False
        self.fields["session_type"].initial = SessionSeries.SessionType.FREE_PRACTICE

    def clean_session_type(self):
        return self.cleaned_data.get("session_type") or SessionSeries.SessionType.FREE_PRACTICE

    class Meta:
        model = SessionSeries
        fields = [
            "label",
            "session_type",
            "default_teacher",
            "weekday",
            "start_time",
            "end_time",
            "default_capacity",
            "is_active",
        ]
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
        self.fields["teacher"].queryset = _teacher_queryset()
        self.fields["session_type"].required = False
        self.fields["session_type"].initial = SessionSeries.SessionType.FREE_PRACTICE

    def clean_session_type(self):
        return self.cleaned_data.get("session_type") or SessionSeries.SessionType.FREE_PRACTICE

    class Meta:
        model = SessionOccurrence
        fields = [
            "series",
            "label",
            "session_date",
            "start_time",
            "end_time",
            "capacity",
            "session_type",
            "teacher",
            "status",
            "notes",
        ]
        widgets = {
            "session_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }


class TeacherOccurrenceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            (SessionOccurrence.Status.OPEN, "Open"),
            (SessionOccurrence.Status.CANCELLED, "Cancelled"),
        ]

    class Meta:
        model = SessionOccurrence
        fields = [
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
