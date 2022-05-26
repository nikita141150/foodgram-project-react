from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models import User, Follow


@admin.register(User)
class UserAdmin(UserAdmin):
    add_fieldsets = (
        (
            None,
            {'fields': (
                'email', 'username', 'first_name',
                'last_name', 'password1', 'password2')}),)
    list_display = ('username', 'email')
    list_filter = ('email', 'username')
    ordering = ('username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
