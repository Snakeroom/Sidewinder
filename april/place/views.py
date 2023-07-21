import struct
from io import BytesIO
from uuid import UUID

import json
import numpy as np
import requests
import random
from PIL import Image
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.http import HttpRequest, JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_safe

from sidewinder.sneknet.wrappers import has_valid_token_or_user
from .models import Project, ProjectDivision, CanvasSettings, ProjectRole


@require_http_methods(['GET'])
@csrf_exempt
def manage_project(request: HttpRequest, uuid):
    if request.method == "GET":

        def to_json(current_project):
            project_permissions = ProjectRole.objects.filter(project=project)

            result = dict(uuid=current_project.uuid,
                          name=current_project.name,
                          featured=current_project.high_priority,
                          can_edit=False)

            project_dimensions = get_project_dimensions(project)
            if project_dimensions:
                result['origin'] = project_dimensions[0:2]
                result['dimensions'] = project_dimensions[2:4]
            else:
                result['origin'] = (None, None)
                result['dimensions'] = (None, None)

            if request.user.is_authenticated:
                result['joined'] = current_project.user_is_member(request.user)

                if current_project.user_is_manager(request.user):
                    result['can_edit'] = True
                    result['members'] = [{"uid": member.user.uid, "username": member.user.username, "role": member.role}
                                         for member in project_permissions]

                    result['divisions'] = [
                        {'uuid': division.uuid, 'name': division.division_name, 'priority': division.priority,
                         'enabled': division.enabled, 'dimensions': division.get_dimensions(),
                         'origin': division.get_origin()} for division in
                        current_project.projectdivision_set.all()]
                else:
                    result['members'] = current_project.get_user_count()
            elif current_project.show_user_count:
                result['members'] = current_project.get_user_count()
            return result

        try:
            project = Project.objects.get(pk=uuid)
            return JsonResponse({'project': to_json(project)}, status=200)
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Project not Found'}, status=404)


def get_project_dimensions(project: Project):
    settings = CanvasSettings.get_solo()
    min_x, min_y = settings.canvas_width, settings.canvas_height
    max_x = max_y = 0

    if project.projectdivision_set.count() == 0:
        return None

    for division in project.projectdivision_set.all():
        x, y = division.get_origin()
        width, height = division.get_dimensions()
        if None in (x, y, width, height):
            return None
        else:
            min_x = min(min_x, x)
            min_y = min(min_y, y)

            max_x = max(max_x, x + width - 1)
            max_y = max(max_y, y + height - 1)

    if min_x > max_x or min_y > max_y:
        return None
    else:
        return min_x, min_y, max_x - min_x + 1, max_y - min_y + 1
    # TODO Simplify this?


@require_safe
def get_projects(request: HttpRequest):
    def to_json(project):
        result = dict(uuid=project.uuid, name=project.name)

        if project.show_user_count:
            result['members'] = project.get_user_count()

        if request.user.is_authenticated:
            result['joined'] = project.user_is_member(request.user)

        project_dimensions = get_project_dimensions(project)

        if project_dimensions:
            result['origin'] = project_dimensions[0:2]
            result['dimensions'] = project_dimensions[2:4]
        else:
            result['origin'] = (None, None)
            result['dimensions'] = (None, None)
        result['featured'] = project.high_priority

        return result

    return JsonResponse({
        "projects": [to_json(project) for project in Project.objects.all()]
    }, status=200)


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
        if project.user_is_member(request.user):
            return JsonResponse({"error": "Already in project"}, status=400)

        ProjectRole(user=request.user, project=project, role='user').save()
    else:
        if not project.user_is_member(request.user):
            return JsonResponse({"error": "Not in project"}, status=400)

        ProjectRole.objects.filter(user=request.user, project=project).delete()

    return JsonResponse({"message": "OK"}, status=200)


@require_http_methods(["POST"])
@csrf_exempt
@has_valid_token_or_user
def create_division(request: HttpRequest, uuid: UUID):
    user = request.snek_token.owner

    # TODO: better permissions
    if not user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        project = Project.objects.get(uuid=uuid)
    except Project.DoesNotExist:
        return JsonResponse({"error": "Project with that UUID does not exist"}, status=404)

    div = ProjectDivision.objects.create(project=project, priority=1)
    return JsonResponse({"message": "Successfully created division", "uuid": div.uuid})


@csrf_exempt
@has_valid_token_or_user
@require_http_methods(['GET'])
def get_divisions(request: HttpRequest, uuid: UUID):
    if hasattr(request, 'snek_token'):
        user = request.snek_token.owner
    else:
        user = request.user

    try:
        project = Project.objects.get(uuid=uuid)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Not Found'}, status=404)

    if project.user_is_manager(user):
        divisions = [
            {'uuid': division.uuid, 'name': division.division_name, 'priority': division.priority,
             'enabled': division.enabled, 'dimensions': division.get_dimensions(),
             'origin': division.get_origin()} for division in
            project.projectdivision_set.all()]
        return JsonResponse({'divisions': divisions}, safe=False)
    else:
        return JsonResponse({'error': 'Forbidden'}, status=403)


@csrf_exempt
@has_valid_token_or_user
@require_http_methods(['GET', 'POST', 'DELETE'])
def manage_division(request, project_uuid: UUID, division_uuid: UUID):
    if hasattr(request, 'snek_token'):
        user = request.snek_token.owner
    else:
        user = request.user

    try:
        project = Project.objects.get(pk=project_uuid)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project with that UUID does not exist'}, status=404)

    if not project.user_is_manager(user):
        return JsonResponse({'error': 'Forbidden'}, status=403)

    try:
        division = ProjectDivision.objects.get(pk=division_uuid, project__uuid=project_uuid)
    except ProjectDivision.DoesNotExist:
        return JsonResponse({'error': 'Division not found'}, status=400)

    if request.method == 'GET':
        result = dict(uuid=division.uuid,
                      name=division.division_name,
                      priority=division.priority,
                      enabled=division.enabled,
                      dimensions=division.get_dimensions(),
                      origin=division.get_origin())
        return JsonResponse({'division': result}, status=200)

    elif request.method == 'POST':
        try:
            body = json.load(request)

            if 'name' in body:
                division.division_name = body['name']

            if 'priority' in body:
                division.priority = body['priority']

            if 'enabled' in body:
                division.enabled = body['enabled']

            if 'origin' in body:
                if not len(body['origin']) == 2 or isinstance(body['origin'], str):
                    return JsonResponse({'error': 'Bad Request'}, status=400)

                division.origin_x = body['origin'][0]
                division.origin_y = body['origin'][1]

            division.save()
            return HttpResponse(status=204)
        except (ValueError, ValidationError):
            return JsonResponse({'error': 'Bad Request'}, status=400)

    elif request.method == 'DELETE':
        division.delete()
        return HttpResponse(status=204)


def blit(source, dest=np.array((1000, 1000)), origin=(0, 0)) -> np.ndarray:
    neg = [-i if i < 0 else 0 for i in origin[::-1]]
    pos = [i if i > 0 else 0 for i in origin[::-1]]
    source_size = np.subtract(dest.shape[0:2], pos)
    source_slice = [slice(neg[i], source_size[i]) for i in (0, 1)]
    source_resized = source[*source_slice]
    dest[pos[0]:pos[0] + source_resized.shape[0], pos[1]:pos[1] + source_resized.shape[1]] = source_resized
    return dest

@has_valid_token_or_user
@require_http_methods(['GET', 'POST', 'DELETE'])
def manage_user(request, uuid: UUID):
    if hasattr(request, 'snek_token'):
        user = request.snek_token.owner
    else:
        user = request.user
    try:
        project = Project.objects.get(pk=uuid)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=400)

    if not project.user_is_manager(user):
        return JsonResponse({'error': 'Forbidden'}, status=403)


@require_safe
def get_bitmap(request: HttpRequest):
    settings = CanvasSettings.get_solo()
    canvas = np.zeros((settings.canvas_width, settings.canvas_height, 4))

    for div in ProjectDivision.objects.filter(project__approved=True):
        if hasattr(div, 'image'):
            empty = np.empty_like(canvas)
            bitmap = np.asarray(Image.open(div.image.image).convert('RGBA'))
            bitmap_resized = blit(bitmap, empty, div.get_origin())
            mask_array = bitmap_resized[:, :, 3] != 0
            np.copyto(canvas, bitmap_resized, where=np.repeat(mask_array[:, :, np.newaxis], 4, axis=2))

    bitmap = Image.fromarray(canvas.astype(np.uint8), 'RGBA')
    io = BytesIO()
    bitmap.save(io, "png")

    io.seek(0)
    return FileResponse(io, filename="bitmap.png", headers={
        "Content-Type": "image/png",
    })


@require_safe
def get_bitmap_for_project(request: HttpRequest, uuid: UUID):
    try:
        project = Project.objects.get(uuid=uuid)
    except Project.DoesNotExist:
        return HttpResponse(b"Project with that UUID does not exist", status=400)

    project_dimensions = get_project_dimensions(project)

    if project_dimensions is None:
        return HttpResponse(b"Project has no image data", status=400)

    project_x, project_y, width, height = project_dimensions

    settings = CanvasSettings.get_solo()
    canvas = np.zeros((settings.canvas_width, settings.canvas_height, 4))
    for div in project.projectdivision_set.all().order_by():
        if hasattr(div, 'image'):
            empty = np.empty_like(canvas)
            bitmap = np.asarray(Image.open(div.image.image).convert('RGBA'))
            bitmap_resized = blit(bitmap, empty, div.get_origin())
            mask_array = bitmap_resized[:, :, 3] != 0
            np.copyto(canvas, bitmap_resized, where=np.repeat(mask_array[:, :, np.newaxis], 4, axis=2))
    origin_x, origin_y, project_width, project_height = project_dimensions
    canvas = canvas[origin_y:origin_y + project_height, origin_x:origin_x + project_width, ...]

    project_bitmap = Image.fromarray(canvas.astype(np.uint8), mode='RGBA')
    io = BytesIO()
    project_bitmap.save(io, "png")

    io.seek(0)
    return FileResponse(io, filename="bitmap.png", headers={
        "Content-Type": "image/png",
    })


@has_valid_token_or_user
@require_http_methods(['GET'])
def get_remediation(request):
    if hasattr(request, 'snek_token'):
        user = request.snek_token.owner
    else:
        user = request.user

    try:
        remediation_response = requests.get('http://localhost:8194/remediations')
    except requests.exceptions.ConnectionError:
        return JsonResponse({'error': 'Gateway Timeout'}, status=504)

    remediations = remediation_response.json()['remediations']

    if not remediations:
        if not any([project.user_is_member(user) for project in Project.objects.all()]):
            return JsonResponse({'message': 'No projects joined'}, status=200)
        else:
            return HttpResponse(status=204)

    remediation_divisions = [pixel['division_uuid'] for pixel in remediations]
    remediation_projects = Project.objects.filter(projectdivision__uuid__in=remediation_divisions, approved=True)
    user_remediation_projects = [project for project in remediation_projects if project.user_is_member(user)]

    if not user_remediation_projects:
        return JsonResponse({'message': 'No projects with remediations found'}, status=200)
    user_remediation_project = random.choice(user_remediation_projects)
    user_remediation_division = ProjectDivision.objects.filter(project=user_remediation_project, enabled=True,
                                                               uuid__in=remediation_divisions).order_by(
        'priority').last()

    if not user_remediation_division:
        return JsonResponse({'message': 'No divisions with remediations found'}, status=200)
    remediation = [remediation for remediation in remediations if
                   UUID(remediation['division_uuid']) == user_remediation_division.uuid][0]

    return JsonResponse({'remediation': remediation}, status=200)


@has_valid_token_or_user
def get_bitmap_for_division(request: HttpRequest, project_uuid: UUID, division_uuid: UUID):
    if hasattr(request, 'snek_token'):
        user = request.snek_token.owner
    else:
        user = request.user

    try:
        project = Project.objects.get(uuid=project_uuid)
    except Project.DoesNotExist:
        return JsonResponse({"error": "Project with that UUID does not exist"}, status=404)

    if project.user_is_manager(user):
        try:
            division = ProjectDivision.objects.get(uuid=division_uuid)

            if hasattr(division, 'image'):
                division_bitmap = Image.open(division.image.image).convert('RGBA')
                io = BytesIO()
                division_bitmap.save(io, "png")
                io.seek(0)
                return FileResponse(io, filename="bitmap.png", headers={
                    "Content-Type": "image/png",
                })
            else:
                return JsonResponse({'error': 'No division bitmap'}, status=404)
        except ProjectDivision.DoesNotExist:
            return JsonResponse({'error': 'Division not found'}, status=400)
    else:
        return JsonResponse({'error': 'Forbidden'}, status=403)
