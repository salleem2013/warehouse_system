from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "email",
            "username",
            "facility",
        )


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
        )


class CustomUserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "facility",
        ]  # Update fields as per your CustomUser model
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "الاسم الأول"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "اسم العائلة"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "البريد الإلكتروني"}
            ),
            "facility": forms.Select(attrs={"class": "form-control", "required": False}),
        }
