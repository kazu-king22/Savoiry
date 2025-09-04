from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        label="名前",
        max_length=150,
        required=True,
    )
    class Meta:
        model = User
        fields = ["first_name", "email", "password1", "password2"]

class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="メールアドレス",
        widget=forms.EmailInput(attrs={"autofocus": True})
    )
