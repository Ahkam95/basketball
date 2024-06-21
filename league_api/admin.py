from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from .models import User, Team, Player, Game, LoginActivity

class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'username','role', 'first_name', 'last_name', 'is_staff', 'login_count', 'total_time_spent']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('username', 'first_name', 'last_name','role')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Statistics'), {'fields': ('login_count', 'total_time_spent')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )

class PlayerInline(admin.TabularInline):
    model = Player
    extra = 0

class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'coach', 'average_score']
    inlines = [PlayerInline]

class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'team', 'height', 'average_score', 'games_played']
    list_filter = ['team']

class GameAdmin(admin.ModelAdmin):
    list_display = ['date', 'team1', 'team2', 'team1_score', 'team2_score', 'winner']
    list_filter = ['team1', 'team2', 'winner']

class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'logout_time']
    list_filter = ['user', 'login_time', 'logout_time']

# Register the models with the admin site
admin.site.register(User, UserAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(LoginActivity, LoginActivityAdmin)
