# accounts/validators.py
# accounts/validators.py
from django.core.exceptions import ValidationError
import re

class AlphaNumericMixValidator:
    """英字と数字の両方を含めるバリデータ"""
    message = "パスワードは英字と数字を少なくとも1文字ずつ含めてください。"

    def validate(self, password, user=None):
        if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            raise ValidationError(self.message)

    def get_help_text(self):
        return self.message


class NotSameAsCurrentPasswordValidator:
    """現在のパスワードと同一の使用を禁止"""
    message = "現在のパスワードと同じものは使用できません。"

    def validate(self, password, user=None):
        if user and user.has_usable_password() and user.check_password(password):
            raise ValidationError(self.message)

    def get_help_text(self):
        return self.message
