from django.contrib import admin
from accounts.models import Users, ColorSet, Templates, ColorCode

# Register your models here.

admin.site.register(Users)
admin.site.register(ColorSet)
admin.site.register(Templates)
admin.site.register(ColorCode)
