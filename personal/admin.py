from django.contrib import admin

# Register your models here.
from .models import Personal


@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    pass