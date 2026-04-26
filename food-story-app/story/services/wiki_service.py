import requests

WIKI_API = "https://ko.wikipedia.org/api/rest_v1/page/summary/{title}"


def search_origin(food_name: str) -> str:
    try:
        res = requests.get(WIKI_API.format(title=food_name), timeout=5)
        if res.status_code == 200:
            return res.json().get("extract", "")
    except Exception:
        pass
    return ""
