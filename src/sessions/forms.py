from django import forms

from .models import SessionOccurrence, SessionSeries


class SessionSeriesForm(forms.ModelForm):
    class Meta:
        model = SessionSeries
        fields = ["label", "weekday", "start_time", "end_time", "default_capacity", "is_active"]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }


class SessionOccurrenceForm(forms.ModelForm):
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
