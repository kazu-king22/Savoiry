from django import forms
from .models import Restaurant, Visit
from django.forms.widgets import  DateInput, ClearableFileInput
from django import forms
from .models import Tag


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
            #"tags",
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
        labels = {'date':'訪問日', 'comment':'感想・思い出', 'rating':'お気に入り度', 'feeling':'評価',}
        widgets = {'date': forms.DateInput(attrs={'type': 'date'}),}


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'category']  
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
