from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

from accounts.identity import build_login_key_from_full_name
from sessions.models import SessionSeries


class NameAuthenticationForm(forms.Form):
    first_name = forms.CharField(label="Prénom", max_length=255)
    last_name = forms.CharField(label="Nom", max_length=255)
    password = forms.CharField(label="Code", widget=forms.PasswordInput)

    error_messages = {
        "invalid_login": "Identifiants invalides ou compte inactif.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        password = cleaned_data.get("password")
        if first_name and last_name and password:
            self.user_cache = authenticate(
                self.request,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            if self.user_cache is None or not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages["invalid_login"])
        return cleaned_data

    def get_user(self):
        return self.user_cache


class AdminAccountCreateForm(forms.Form):
    full_name = forms.CharField(label="Nom complet", max_length=255)
    email = forms.EmailField(label="Email", required=False)
    role = forms.ChoiceField(label="Parcours", choices=get_user_model().Role.choices)
    is_responsable_accredited = forms.TypedChoiceField(
        label="Accréditation référent",
        choices=(("true", "responsable"), ("false", "non")),
        coerce=lambda value: value == "true",
        initial="false",
    )
    has_orange_passport = forms.TypedChoiceField(
        label="Passport orange",
        choices=(("true", "passport orange"), ("false", "sans passport")),
        coerce=lambda value: value == "true",
        initial="false",
    )
    is_active = forms.TypedChoiceField(
        label="Activation du compte",
        choices=(("true", "actif"), ("false", "inactif")),
        coerce=lambda value: value == "true",
        initial="true",
    )
    course_series_ids = forms.ModelMultipleChoiceField(
        label="Cours rattachés",
        queryset=SessionSeries.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course_series_ids"].queryset = SessionSeries.objects.filter(
            session_type=SessionSeries.SessionType.COURSE
        ).order_by("label")

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()
        login_key = build_login_key_from_full_name(full_name)
        if get_user_model().objects.filter(login_key=login_key).exists():
            raise forms.ValidationError("Un compte existe deja pour ce prénom et nom.")
        return full_name

    def clean_email(self):
        email = (self.cleaned_data["email"] or "").strip().lower()
        if not email:
            return None
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte existe deja pour cet email.")
        return email


class RequiredPasswordChangeForm(PasswordChangeForm):
    email = forms.EmailField(label="Email")
    old_password = forms.CharField(label="Code temporaire", widget=forms.PasswordInput)
    new_password1 = forms.CharField(label="Nouveau code", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Confirmer le nouveau code", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].initial = self.user.email or ""

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if (
            get_user_model()
            .objects.exclude(pk=self.user.pk)
            .filter(email__iexact=email)
            .exists()
        ):
            raise forms.ValidationError("Un compte existe deja pour cet email.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class BulkAccountImportForm(forms.Form):
    roster_data = forms.CharField(
        label="Tableau adhérents",
        widget=forms.Textarea(attrs={"rows": 14, "spellcheck": "false"}),
    )
