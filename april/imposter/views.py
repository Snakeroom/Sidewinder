import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from april.imposter.models import KnownAnswer, MasterSwitch
from april.imposter.wrappers import check_can_query
from sidewinder.sneknet.wrappers import has_valid_token_or_user


@csrf_exempt
@has_valid_token_or_user
@require_http_methods(["POST"])
def submit_known_answers(request: HttpRequest):
    switch = MasterSwitch.get_solo()
    if not switch.enable_all:
        return JsonResponse({"error": "Temporarily disabled"}, status=503)

    body = json.load(request)

    if "options" not in body:
        return JsonResponse({"error": "Missing 'options' key"}, status=400)

    if hasattr(request, 'snek_token'):
        submitter = request.snek_token.owner
    else:
        submitter = request.user

    seen = {}
    update_list = []
    for option_obj in body["options"]:
        message = option_obj["message"]
        correct = option_obj["correct"]

        answer, created = KnownAnswer.objects.get_or_create(
            message=message,
            defaults=dict(correct=correct, submitted_by=submitter, submission_tag=body.get("tag", None),
                          question_number=switch.question_number),
        )
        answer.seen_times += 1
        if switch.enable_imposter_flipping and not correct:
            answer.correct = False  # Flips impostor to human but not the other way round

        update_list.append(answer)

        seen[answer.pk] = {
            "seen": not created,
            "message": answer.message,
        }

    KnownAnswer.objects.bulk_update(update_list, ('seen_times', 'correct',))

    return JsonResponse({
        "seen": seen,
    })

@csrf_exempt
@check_can_query
@require_http_methods(["POST"])
def query_answers(request: HttpRequest):
    switch = MasterSwitch.get_solo()
    if not switch.enable_queries or not switch.enable_all:
        return JsonResponse({"error": "Querying temporarily disabled"}, status=503)

    body = json.load(request)

    if "options" not in body:
        return JsonResponse({"error": "Missing 'options' key"}, status=400)

    answers = []
    for i, opt in enumerate(body["options"]):
        try:
            answer = KnownAnswer.objects.get(message__exact=opt)

            answers.append({
                "i": i,
                "message": answer.message,
                "correct": answer.correct,
            })
        except KnownAnswer.DoesNotExist:
            continue
        except KnownAnswer.MultipleObjectsReturned:
            continue  # oh no

    should_lie = switch.enable_five_human_hiding or ('hide_five' in request.GET)
    human_answers = [answer for answer in answers if not answer['correct']]
    if should_lie and len(human_answers) == 5:
        answers = answers[:-2]

    return JsonResponse({"answers": answers})

@require_http_methods(["GET", "HEAD"])
def fetch_recent(request: HttpRequest):
    if not MasterSwitch.get_solo().enable_all:
        return JsonResponse({"error": "Temporarily disabled"}, status=503)

    recent_answers = KnownAnswer.objects.order_by('-updated_at')[:5]

    res = []
    for answer in recent_answers:
        res.append({
            "id": answer.pk,
            "message": answer.message,
            "correct": answer.correct,
            "created": answer.created_at,
            "modified": answer.updated_at,
        })

    return JsonResponse({"recent": res})

@require_http_methods(["GET", "HEAD"])
def check_answer(request: HttpRequest):
    if not MasterSwitch.get_solo().enable_all:
        return JsonResponse({"error": "Temporarily disabled"}, status=503)

    if 'q' not in request.GET:
        return JsonResponse({"error": "Missing query"}, status=400)

    query = request.GET['q']
    try:
        answer = KnownAnswer.objects.get(message__exact=query)

        return JsonResponse({
            "found": True,
            "answer": {
                "message": answer.message,
                "correct": answer.correct,
            }
        })
    except KnownAnswer.DoesNotExist:
        return JsonResponse({
            "found": False,
            "answer": None
        })
