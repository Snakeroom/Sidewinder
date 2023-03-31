from django.http import HttpRequest, JsonResponse

# from april.imposter.models import MasterSwitch
from sidewinder.sneknet.models import Token


def _check_authorized(request: HttpRequest, view_func, kwargs):
    if request.user.is_authenticated:
        if not request.user.is_active:
            return JsonResponse({"error": "Account deactivated."}, status=403)

        return view_func(request, **kwargs)

    if 'authorization' in request.headers:
        token = request.headers['authorization']
    elif 'token' in request.GET:
        token = request.GET['token']
    else:
        return JsonResponse({"error": "No token provided!"}, status=401)

    try:
        perm = Token.objects.get(token=token)
        if not perm.active:
            return JsonResponse({"error": "Token deactivated"}, status=403)

        if perm.whitelisted_address is not None:
            if perm.whitelisted_address != request.headers['X-Real-Ip']:
                return JsonResponse({"error": "Token not valid for this address"}, status=403)
    except Token.DoesNotExist:
        return JsonResponse({"error": "Invalid token!"}, status=403)

    request.snek_token = perm
    return view_func(request, **kwargs)


def has_valid_token_or_user(view_func):
    def wrapper(request: HttpRequest, **kwargs):
        return _check_authorized(request, view_func, kwargs)

    return wrapper


def check_can_query(view_func):
    def wrapper(request: HttpRequest):
        # if MasterSwitch.get_solo().disable_unauthorized_queries:
        #     return _check_authorized(request, view_func)
        # else:
        return view_func(request)

    return wrapper
