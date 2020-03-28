from django.contrib.auth import login
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from praw import Reddit

from sidewinder.identity.models import RedditApplication, User, RedditCredentials
from sidewinder.utils import generate_state_token


def _build_reddit(request: HttpRequest) -> Reddit:
    app = RedditApplication.get_solo()
    return Reddit(client_id=app.client_id, client_secret=app.client_secret,
                  redirect_uri=request.build_absolute_uri(reverse(authorize_callback)),
                  user_agent='Sidewinder/1.0.0')


def reddit_login(request: HttpRequest):
    reddit = _build_reddit(request)

    state = generate_state_token()
    redirect_url = reddit.auth.url(['identity'], state)

    request.session['state'] = state

    return HttpResponseRedirect(redirect_url)


def authorize_callback(request: HttpRequest):
    reddit = _build_reddit(request)

    if 'error' in request.GET:
        error_msg = request.GET['error']

        return  # TODO: handle error

    if request.GET['state'] != request.session['state']:
        return JsonResponse({"error": "invalid state"})

    code = request.GET['code']
    refresh_token = reddit.auth.authorize(code)
    reddit_user = reddit.user.me()

    try:
        user = User.objects.get(uid=reddit_user.id)
        login(request, user)

        # noinspection PyProtectedMember
        access_token = reddit._authorized_core._authorizer.access_token

        creds, created = RedditCredentials.objects.get_or_create(
            user=user,
            defaults=dict(access_token=access_token, refresh_token=refresh_token, last_refresh=timezone.now())
        )

        if not created:
            creds.access_token = access_token
            creds.refresh_token = refresh_token
            creds.last_refresh = timezone.now()
            creds.save()
    except User.DoesNotExist:
        pass  # TODO: auto sign up

    return HttpResponse(b"success, probably")
