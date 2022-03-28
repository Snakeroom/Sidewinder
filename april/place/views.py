from uuid import UUID

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_safe

from .models import Project

@require_safe
def get_projects(request: HttpRequest):
    def to_json(project):
        result = dict(uuid=project.uuid, name=project.name)

        if project.show_user_count:
            result['members'] = project.users.count()

        if request.user.is_authenticated:
            result['joined'] = project.users.contains(request.user)

        return result

    return JsonResponse({
        "projects": [to_json(project) for project in Project.objects.all()]
    })

@require_http_methods(["PUT", "DELETE"])
@csrf_exempt
def join_project(request: HttpRequest, uuid: UUID):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    try:
        project = Project.objects.get(uuid=uuid)
    except Project.DoesNotExist:
        return JsonResponse({"error": "Project with that UUID doesn't exist!"}, status=400)

    if request.method == "PUT":
        if project.users.contains(request.user):
            return JsonResponse({"error": "Already in project"}, status=400)

        project.users.add(request.user)
    else:
        if not project.users.contains(request.user):
            return JsonResponse({"error": "Not in project"}, status=400)

        project.users.remove(request.user)

    return JsonResponse({"message": "OK"}, status=200)
