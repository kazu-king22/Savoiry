from django import forms
from .models import Restaurant, Visit
from django.forms.widgets import  DateInput, ClearableFileInput


# 画像を複数アップロードできるようにするカスタムWidget
class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = [
            "store_name",
            "url",
            "area",
            "genre",
            "companions",
            "scene",
            "holiday",
            "tags",
        ]


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['date', 'comment', 'rating', 'feeling']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
