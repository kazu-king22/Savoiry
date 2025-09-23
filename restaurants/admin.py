from django.contrib import admin
from .models import Restaurant, Visit, VisitImage, Tag

admin.site.register(Restaurant)
admin.site.register(Visit)
admin.site.register(VisitImage)
admin.site.register(Tag)

# Register your models here.
