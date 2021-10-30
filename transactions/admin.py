from django.contrib import admin

# Register your models here.
from transactions.models import FBATransaction

admin.site.register(FBATransaction)