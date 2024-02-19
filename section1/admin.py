from django.contrib import admin

# Register your models here.
from .models import Quarter, Month, Family, Adult, Child

class QuarterAdmin(admin.ModelAdmin):
    list_display = ("report_quarter", "start_date", "end_date")

class FamilyAdmin(admin.ModelAdmin):
    list_display = '__all__'

class AdultAdmin(admin.ModelAdmin):
    list_display = '__all__'

admin.site.register(Quarter)
admin.site.register(Family)
admin.site.register(Adult)
