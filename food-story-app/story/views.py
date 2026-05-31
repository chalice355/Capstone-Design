import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services.llm_service import get_all_tabs
from .services.wiki_service import search_origin
from .services.vision_service import identify_food
from .models import Diary


def health(request):
    return JsonResponse({"status": "ok"})


def story(request, food_name):
    wiki_text = search_origin(food_name)
    tabs = get_all_tabs(food_name)
    if wiki_text and "유래" in tabs:
        tabs["유래"] = wiki_text + "\n\n" + tabs["유래"]
    return JsonResponse(
        {"food_name": food_name, "tabs": tabs},
        json_dumps_params={"ensure_ascii": False},
    )


@csrf_exempt
@require_http_methods(["POST"])
def predict(request):
    image_file = request.FILES.get("image")
    if not image_file:
        return JsonResponse({"error": "이미지가 없습니다."}, status=400)

    media_type = image_file.content_type
    if not media_type or media_type == "application/octet-stream":
        name = image_file.name or ""
        media_type = "image/png" if name.lower().endswith(".png") else "image/jpeg"
    food_name = identify_food(image_file.read(), media_type)

    if food_name == "알수없음":
        return JsonResponse({"error": "음식을 인식하지 못했습니다."}, status=422)

    return JsonResponse(
        {"food_name": food_name},
        json_dumps_params={"ensure_ascii": False},
    )


@csrf_exempt
@require_http_methods(["GET", "POST"])
def diary_list(request):
    if request.method == "GET":
        diaries = list(
            Diary.objects.values("id", "food_name", "place", "date", "tabs_json")
        )
        return JsonResponse(diaries, safe=False, json_dumps_params={"ensure_ascii": False})

    data = json.loads(request.body)
    diary = Diary.objects.create(
        food_name=data["food_name"],
        place=data.get("place", ""),
        date=data["date"],
        tabs_json=data["tabs_json"],
    )
    return JsonResponse({"id": diary.id}, status=201)


@csrf_exempt
@require_http_methods(["DELETE"])
def diary_detail(request, pk):
    Diary.objects.filter(pk=pk).delete()
    return JsonResponse({"ok": True})
