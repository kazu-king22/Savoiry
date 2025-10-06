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
        labels = {
            "store_name": "店舗名",
            "url": "URL",
            "area": "エリア",
            "genre": "ジャンル",
            "companions": "同行者",
            "scene": "シーン",
            "holiday": "定休日",
            "tags": "タグ",
        }


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['date', 'comment', 'rating', 'feeling']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

from django import forms
from .models import Tag

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'category']  # ← category を追加！
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
