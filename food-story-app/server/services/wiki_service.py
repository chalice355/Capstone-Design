import requests

WIKI_API = "https://ko.wikipedia.org/api/rest_v1/page/summary/{title}"


def search_origin(food_name: str) -> str:
    """음식명으로 위키피디아 요약 검색"""
    try:
        res = requests.get(WIKI_API.format(title=food_name), timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("extract", "")
    except Exception:
        pass
    return ""
