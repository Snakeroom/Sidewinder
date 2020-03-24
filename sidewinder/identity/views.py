from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from praw import Reddit

from sidewinder.identity.models import RedditApplication
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
    reddit.auth.authorize(code)

    return JsonResponse({"username": reddit.user.me().name})
