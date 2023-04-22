import requests

from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from praw import Reddit
from requests.models import PreparedRequest

from sidewinder.identity.models import RedditApplication, DiscordApplication, User, RedditCredentials, DiscordCredentials
from sidewinder.utils import generate_state_token

def _build_reddit(request: HttpRequest) -> Reddit:
    app = RedditApplication.get_solo()
    return Reddit(client_id=app.client_id, client_secret=app.client_secret,
                  redirect_uri=request.build_absolute_uri(reverse(reddit_authorize_callback)),
                  user_agent='Sidewinder/1.0.0')


def reddit_login(request: HttpRequest):
    reddit = _build_reddit(request)

    state = generate_state_token()
    redirect_url = reddit.auth.url(['identity'], state)

    if 'return_to' in request.GET:
        request.session['return_to'] = request.GET['return_to']

    request.session['state'] = state

    return HttpResponseRedirect(redirect_url)

def discord_login(request: HttpRequest):
    app = DiscordApplication.get_solo()

    state = generate_state_token()

    redirect = PreparedRequest()
    redirect.prepare_url("https://discord.com/api/oauth2/authorize", {
        'response_type': 'code',
        'client_id': app.client_id,
        'scope': 'identify',
        'state': state,
        'redirect_uri': request.build_absolute_uri(reverse(discord_authorize_callback)),
        'prompt': 'none'
    })

    if 'return_to' in request.GET:
        request.session['return_to'] = request.GET['return_to']

    request.session['state'] = state

    return HttpResponseRedirect(redirect.url)

def reddit_authorize_callback(request: HttpRequest):
    reddit = _build_reddit(request)
    redirect_to = "/"

    if 'return_to' in request.session:
        redirect_to = request.session['return_to']
    redirect_to = request.build_absolute_uri(redirect_to)

    if 'error' in request.GET:
        error_msg = request.GET['error']
        messages.error(request, f"Couldn't sign you in with Reddit: {error_msg}")

        return HttpResponseRedirect(redirect_to)

    if request.GET['state'] != request.session['state']:
        messages.error(request, "Couldn't sign you in with Reddit: invalid state parameter")

        return HttpResponseRedirect(redirect_to)

    code = request.GET['code']
    refresh_token = reddit.auth.authorize(code)
    reddit_user = reddit.user.me()

    try:
        user = User.objects.get(uid=reddit_user.id)
    except User.DoesNotExist:
        user = User.objects.create_user(reddit_user.name, uid=reddit_user.id)

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

    return HttpResponseRedirect(redirect_to)


def discord_authorize_callback(request: HttpRequest):
    redirect_to = "/"

    if 'return_to' in request.session:
        redirect_to = request.session['return_to']
    redirect_to = request.build_absolute_uri(redirect_to)

    if not request.user.is_authenticated:
        messages.error(request, 'Not signed in')

        return HttpResponseRedirect(redirect_to)

    if 'error' in request.GET:
        error_msg = request.GET['error']
        messages.error(request, f"Couldn't authorize you with Discord: {error_msg}")

        return HttpResponseRedirect(redirect_to)

    if request.GET['state'] != request.session['state']:
        messages.error(request, "Couldn't authorize you with Discord: invalid state parameter")

        return HttpResponseRedirect(redirect_to)

    code = request.GET['code']

    app = DiscordApplication.get_solo()

    token_response = requests.post('https://discord.com/api/v10/oauth2/token', data={
        'client_id': app.client_id,
        'client_secret': app.client_secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': request.build_absolute_uri(reverse(discord_authorize_callback)),
    }, headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Sidewinder/1.0.0'
    }).json()

    if 'error' in token_response:
        error_msg = token_response['error']
        messages.error(request, f"Couldn't authorize you with Discord: failed to get token: {error_msg}")

        return HttpResponseRedirect(redirect_to)

    refresh_token = token_response['refresh_token']
    access_token = token_response['access_token']

    user_response = requests.get('https://discord.com/api/v10/users/@me', headers={
        'Authorization': 'Bearer ' + access_token,
        'User-Agent': 'Sidewinder/1.0.0'
    }).json()

    if 'error' in user_response:
        error_msg = user_response['error']
        messages.error(request, f"Couldn't authorize you with Discord: failed to identify user: {error_msg}")

        return HttpResponseRedirect(redirect_to)

    id = user_response['id']

    if request.user.discord_id != '' and request.user.discord_id != id:
        messages.error(request, f"Couldn't authorize you with Discord: mismatched user")

        return HttpResponseRedirect(redirect_to)

    request.user.discord_id = id
    request.user.save(update_fields=['discord_id'])

    creds, created = DiscordCredentials.objects.get_or_create(
        user=request.user,
        defaults=dict(access_token=access_token, refresh_token=refresh_token, last_refresh=timezone.now())
    )

    if not created:
        creds.access_token = access_token
        creds.refresh_token = refresh_token
        creds.last_refresh = timezone.now()
        creds.save()

    return HttpResponseRedirect(redirect_to)

def get_current_user(request):
    if request.user.is_authenticated:
        user: User = request.user

        return JsonResponse({
            "uid": user.uid,
            "username": user.username,
            "pronouns": user.pronouns,
            "discord_id": user.discord_id,
            "is_staff": user.is_staff,
        })
    else:
        return JsonResponse({
            "error": "Not signed in"
        }, status=401)


@require_POST
@csrf_exempt
def edit_profile(request):
    if request.user.is_anonymous:
        return JsonResponse({
            "error": "Not signed in."
        }, status=401)

    try:
        pronouns = request.POST['pronouns']

        request.user.pronouns = str(pronouns)
    except KeyError:
        pass

    request.user.save(update_fields=['pronouns'])

    return HttpResponse(status=204)
