from django.http import HttpRequest, JsonResponse

from sidewinder.sneknet.models import Token


def has_valid_token(view_func):
    def wrapper(request: HttpRequest):
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
        return view_func(request)

    return wrapper
