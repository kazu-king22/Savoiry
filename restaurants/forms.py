from django import forms
from .models import Restaurant, Visit
from django.forms.widgets import  DateInput, ClearableFileInput
from django import forms
from .models import Tag
from django.utils import timezone
import datetime

class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True


class RestaurantForm(forms.ModelForm):
    holiday = forms.MultipleChoiceField(
        choices=Restaurant.DAY_CHOICES,
         widget=forms.SelectMultiple(attrs={
            "class": "input-field",  # ← ここを追加（共通スタイル指定）
        }),
        required=False,
        label="休業日"
     )
    
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
        
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["store_name"].widget.attrs["placeholder"] = "例：中華そば○○"
        self.fields["url"].widget.attrs["placeholder"] = "例：https://example.com"
        self.fields["area"].widget.attrs["placeholder"] = "例：渋谷・天神など"
        self.fields["genre"].widget.attrs["placeholder"] = "例：ラーメン・カフェなど"
        self.fields["companions"].widget.attrs["placeholder"] = "例：友人・家族など"
        self.fields["scene"].widget.attrs["placeholder"] = "例：ランチ・デートなど"
        
        for field_name in ["store_name", "url", "area", "genre", "companions", "scene"]:
            self.fields[field_name].widget.attrs["autocomplete"] = "on"
        

class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['date', 'comment', 'rating', 'feeling']
        labels = {
            'date': '訪問日',
            'comment': '感想・思い出',
            'rating': 'お気に入り度',
            'feeling': '評価',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].required = False

    # ★ 未来日チェックを追加（最重要） ★
    def clean_date(self):
        visit_date = self.cleaned_data.get("date")

        if not visit_date:
            return visit_date  # 未入力はOK（後でビューで今日を補完してる場合もある）

        today = timezone.localdate()

        if visit_date > today:
            raise forms.ValidationError("今日より先は登録できません。")

        return visit_date



class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'category']  
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }