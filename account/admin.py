from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import MyUser, Balance, Transfer

admin.site.register(MyUser, UserAdmin)
admin.site.register(Balance)
admin.site.register(Transfer)