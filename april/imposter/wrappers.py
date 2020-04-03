from django.http import HttpRequest

from april.imposter.models import MasterSwitch
from sidewinder.sneknet.wrappers import _check_authorized


def check_can_query(view_func):
    def wrapper(request: HttpRequest):
        if MasterSwitch.get_solo().disable_unauthorized_queries:
            return _check_authorized(request, view_func)
        else:
            return view_func(request)

    return wrapper
