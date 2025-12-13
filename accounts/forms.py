from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django import forms
from django.core.exceptions import ValidationError

User = get_user_model()

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        label="名前",
        max_length=150,
        required=True,
        widget=forms.TextInput
    )

    email = forms.EmailField(
        label="メールアドレス",
        required=True,
        widget=forms.EmailInput,
        error_messages={
            "invalid": "有効なメールアドレスの形式で入力してください。",
            "required": "メールアドレスを入力してください。",
        },
    )

    password1 = forms.CharField(
        label="パスワード",
        required=True,
        widget=forms.PasswordInput(
        attrs={
            "placeholder": "8文字以上・英数字を含む"
        }
    ),
        error_messages={
            "required": "パスワードを入力してください。",
        },
    )

    password2 = forms.CharField(
        label="パスワード（確認）",
        required=True,
         widget=forms.PasswordInput(
        attrs={
            "placeholder": "確認のため、もう一度入力"
        }
    ),
        error_messages={
            "required": "パスワード(確認)を入力してください。",
        },
    )

    class Meta:
        model = User
        fields = ["first_name", "email", "password1", "password2"]
    
    
class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="メールアドレス",
        widget=forms.EmailInput(attrs={"autofocus": True})
    )


class EmailChangeForm(forms.ModelForm):
    confirm_email = forms.EmailField(
        label='新しいメールアドレス（確認）',
        required=True,
        error_messages={
            "required": "すべての項目を入力してください。",
            "invalid": "有効なメールアドレスの形式で入力してください。",
        },
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ['email']
        labels = {'email': '新しいメールアドレス'}
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
            }),
        }
        error_messages = {
            'email': {
                "required": "すべての項目を入力してください。",
                "invalid": "有効なメールアドレスの形式で入力してください。",
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].initial = None
        self.fields['confirm_email'].initial = None
        self.fields['email'].widget.attrs.update({
            'autocomplete': 'off',
            'value': '',
        })
        self.fields['confirm_email'].widget.attrs.update({
            'autocomplete': 'off',
            'value': '',
        })


    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')

        if not email or not confirm_email:
            if not email:
                self.add_error('email', 'すべての項目を入力してください。')
            if not confirm_email:
                self.add_error('confirm_email', 'すべての項目を入力してください。')
            return cleaned_data

        if email != confirm_email:
            self.add_error('confirm_email', '新しいメールアドレスと確認用が一致していません。')

        return cleaned_data


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

        self.fields['old_password'].label = "現在のパスワード"
        self.fields['new_password1'].label = "新しいパスワード"
        self.fields['new_password2'].label = "新しいパスワード（確認）"
        
        self.fields['old_password'].widget.attrs.update({
            'placeholder': '現在のパスワードを入力'
        })
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': '8文字以上・英数字を含む'
        })
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': '確認のため、もう一度入力'
        })

        self.fields['old_password'].error_messages.update({
            'required': "現在のパスワードを入力してください。",
        })
        self.fields['new_password1'].error_messages.update({
            'required': "新しいパスワードを入力してください。",
            'min_length': "パスワードは8文字以上で入力してください。",
        })
        self.fields['new_password2'].error_messages.update({
            'required': "確認用パスワードを入力してください。",
        })

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError("現在のパスワードが正しくありません。")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error('new_password2', "新しいパスワードが一致していません。")

        return cleaned_data