import json

from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core import serializers

from april.imposter.models import KnownAnswer


@csrf_exempt
@require_http_methods(["POST"])
def submit_known_answers(request: HttpRequest):
    body = json.load(request)

    if "options" not in body:
        return JsonResponse({"error": "Missing 'options' key"}, status=400)

    seen = {}
    for option_obj in body["options"]:
        message = option_obj["message"]
        correct = option_obj["correct"]

        answer, created = KnownAnswer.objects.get_or_create(message=message, defaults=dict(correct=correct))
        answer.seen_times += 1
        answer.save()

        seen[answer.pk] = {
            "seen": not created,
            "message": answer.message,
        }

    return JsonResponse({
        "seen": seen,
    })

@csrf_exempt
@require_http_methods(["POST"])
def query_answers(request: HttpRequest):
    body = json.load(request)

    if "options" not in body:
        return JsonResponse({"error": "Missing 'options' key"}, status=400)

    answers = []
    for i, opt in enumerate(body["options"]):
        try:
            answer = KnownAnswer.objects.get(message__iexact=opt)

            answers.append({
                "i": i,
                "message": answer.message,
                "correct": answer.correct,
            })
        except KnownAnswer.DoesNotExist:
            continue
        except KnownAnswer.MultipleObjectsReturned:
            continue  # oh no

    return JsonResponse({"answers": answers})

@require_http_methods(["GET", "HEAD"])
def fetch_recent(request: HttpRequest):
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
    if 'q' not in request.GET:
        return JsonResponse({"error": "Missing query"}, status=400)

    query = request.GET['q']
    try:
        answer = KnownAnswer.objects.get(message__iexact=query)

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
