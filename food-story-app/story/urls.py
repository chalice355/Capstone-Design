from django.urls import path
from . import views

urlpatterns = [
    path("", views.health),
    path("predict/", views.predict),
    path("story/<str:food_name>/", views.story),
    path("diary/", views.diary_list),
    path("diary/<int:pk>/", views.diary_detail),
]
