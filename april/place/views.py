import struct
from io import BytesIO
from uuid import UUID

from PIL import Image
from django.http import HttpRequest, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_safe

from sidewinder.sneknet.wrappers import has_valid_token_or_user
from .models import Project, ProjectDivision, PALETTE

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

@require_http_methods(["POST"])
@csrf_exempt
@has_valid_token_or_user
def create_division(request: HttpRequest, project_uuid: UUID):
    user = request.snek_token.owner

    # TODO: better permissions
    if not user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        project = Project.objects.get(uuid=project_uuid)
    except Project.DoesNotExist:
        return JsonResponse({"error": "Project with that UUID does not exist"}, status=404)

    image_bin = request.body

    # Validate
    try:
        x, y, width, height = struct.unpack(">HHHH", image_bin[:8])

        if len(image_bin) != (width * height) + 8:
            return JsonResponse({"error": "Snek image has invalid dimensions or is truncated"}, status=400)
    except struct.error as err:
        return JsonResponse({"error": "Invalid snek image", "message": err.args[0]}, status=400)

    div = ProjectDivision.objects.create(project=project, priority=1, content=image_bin)
    return JsonResponse({"message": "Successfully created division", "uuid": div.uuid})

def split_rgb(rgb):
    return rgb >> 16, rgb >> 8 & 0xFF, rgb & 0xFF, 0xFF  # alpha 255

@require_safe
def get_bitmap(request: HttpRequest):
    canvas = Image.new('RGBA', (1000, 1000), (255, 255, 255, 0))

    for div in ProjectDivision.objects.all():
        ox, oy = div.get_origin()
        width, height = div.get_dimensions()

        for y in range(0, height):
            for x in range(0, width):
                index = (width * y) + x
                colour_index = div.get_image_bytes()[index]
                if colour_index == 0xFF:
                    continue

                rgb = PALETTE[colour_index]
                canvas.putpixel((ox + x, oy + y), split_rgb(rgb))

    io = BytesIO()
    canvas.save(io, "png")

    io.seek(0)
    return FileResponse(io, filename="bitmap.png", headers={
        "Content-Type": "image/png",
    })
