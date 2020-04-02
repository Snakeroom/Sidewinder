from django.contrib import admin
from solo.admin import SingletonModelAdmin

from sidewinder.sneknet.models import ScienceLog, Token, MasterSwitch

import string
import random

_pool = string.digits + string.ascii_letters
def generate_token():
    return "".join(random.choices(_pool, k=56))

@admin.register(ScienceLog)
class ScienceLogAdmin(admin.ModelAdmin):
    list_display = ('user_hash', 'total_actions',)

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('friendly_name', 'active',)
    list_filter = ('active',)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)

        initial['token'] = generate_token()

        return initial

@admin.register(MasterSwitch)
class MasterSwitchAdmin(SingletonModelAdmin):
    pass
