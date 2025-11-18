from django.contrib import admin
from .models import Restaurant, Visit, VisitImage, Tag, SuggestWord

admin.site.register(Restaurant)
admin.site.register(Visit)
admin.site.register(VisitImage)
admin.site.register(Tag)
admin.site.register(SuggestWord)

# Register your models here.
