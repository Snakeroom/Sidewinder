from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.forms import UserChangeForm, AdminPasswordChangeForm
from django.urls import path
from solo.admin import SingletonModelAdmin

from sidewinder.identity.models import User, RedditCredentials, RedditApplication


class IdentityUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = IdentityUserChangeForm
    list_display = ('username', 'uid', 'pronouns',)
    readonly_fields = ('uid',)
    change_password_form = AdminPasswordChangeForm
    change_user_password_template = None

    fieldsets = (
        ('User details', {
            "fields": ('username', 'uid', 'password', 'date_joined',)
        }),
        ('Profile', {
            "fields": ('email', 'pronouns',)
        }),
        ('Permissions', {
            "fields": ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',)
        }),
    )

    def get_urls(self):
        return [
            path('<id>/password/',
                 self.admin_site.admin_view(auth_admin.UserAdmin.user_change_password.__get__(self, self.__class__)),
                 name='auth_user_password_change')
        ] + super().get_urls()

    def lookup_allowed(self, lookup, value):
        # Don't allow lookups involving passwords.
        return not lookup.startswith('password') and super().lookup_allowed(lookup, value)

@admin.register(RedditApplication)
class RedditAppAdmin(SingletonModelAdmin):
    list_display = ('name',)

@admin.register(RedditCredentials)
class RedditCredentialsAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_refresh',)
