from django.http import JsonResponse
from .services.llm_service import get_all_tabs
from .services.wiki_service import search_origin


def health(request):
    return JsonResponse({"status": "ok"})


def story(request, food_name):
    wiki_text = search_origin(food_name)
    tabs = get_all_tabs(food_name)
    if wiki_text and "유래" in tabs:
        tabs["유래"] = wiki_text[:300] + "\n\n" + tabs["유래"]
    return JsonResponse({"food_name": food_name, "tabs": tabs}, json_dumps_params={"ensure_ascii": False})
