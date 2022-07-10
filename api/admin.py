from django.contrib import admin
from django.utils.translation import gettext as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Game, HighScore, Move, User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    inlines = (UserProfileInline,)


admin.site.register(UserProfile)
admin.site.register(HighScore)
admin.site.register(Game)
admin.site.register(Move)
