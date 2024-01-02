from channels.generic.websocket import JsonWebsocketConsumer
from django.http import JsonResponse
from django.utils import timezone
from django_redis import get_redis_connection

from .models import UserState, RoundState

SECOND_CHANNEL = "second:active"

def report(socket: JsonWebsocketConsumer, content):
    user = socket.scope['user']

    if not user.is_authenticated:
        socket.send_json({"error": "Not authenticated.", 'code': 'not_authenticated'})
        return

    if 'won' not in content:
        return

    did_win = content['won']
    user.state.last_was_win = did_win
    if did_win:
        user.state.wins += 1
        user.state.current_streak += 1
    else:
        user.state.losses += 1
        user.state.current_streak = 0

    user.state.save()

def keepalive(socket: JsonWebsocketConsumer, content):
    user = socket.scope['user']

    if not user.is_authenticated:
        socket.send_json({"error": "Not authenticated.", 'code': 'not_authenticated'})
        return

    round_state = RoundState.get_solo()
    conn = get_redis_connection()
    state: UserState = user.state

    state.last_active = timezone.now()
    state.current_channel = socket.channel_name

    status = conn.get("second_round_status")
    cur_round_id = int(conn.get("second_round_id"))

    if round_state.round_id != cur_round_id:
        round_state.clear()
        round_state.round_id = cur_round_id

    if status == "inactive":
        return JsonResponse({"error": "Round not active.", 'code': 'round_inactive'}, status=400)

    # Partition active users into two lists:
    # - People voting 1st (51%)
    # - People voting 2nd (49%)
    # ratio 49/51 = 0.961

    cur_ratio = round_state.ratio()
    prefer_streaks = state.user.preferences.prefer_streaks

    # vote_second True means they win, False means they lose
    if state.losses < 30:
        # Force some losses for n00bs
        vote_second = False
    elif state.current_streak > 5 and prefer_streaks:
        vote_second = True
    elif prefer_streaks:
        vote_second = False
    elif state.losses > state.wins and cur_ratio < 0.85:
        vote_second = True
    elif cur_ratio > 49 / 51:
        vote_second = False
    else:
        vote_second = True

    if vote_second:
        round_state.second_count += 1
        img_id = conn.get("second_current_first")
    else:
        round_state.first_count += 1
        img_id = conn.get("second_current_second")

    socket.send_json({
        "type": "second:vote",
        "select_id": int(img_id),
    })

    round_state.save()
    state.save(update_fields=['last_active', 'current_channel'])
