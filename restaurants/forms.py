from django import forms
from .models import Restaurant, Visit, VisitImage
from django.forms.widgets import FileInput


class MultiFileInput(FileInput):
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
    images = forms.FileField(
        widget=MultiFileInput(attrs={'multiple': True}),
        required=False,
        label="写真"
    )
    
    class Meta:
        model = Visit
        fields = [
            "date", 
            "comment", 
            "rating", 
            "feeling",
        ] 