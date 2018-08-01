from django.contrib import admin

from .models import Dog, UserDog, UserPref


admin.site.register(Dog)
admin.site.register(UserDog)
admin.site.register(UserPref)
