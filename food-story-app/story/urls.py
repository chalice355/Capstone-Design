from django.urls import path
from . import views

urlpatterns = [
    path("", views.health),
    path("story/<str:food_name>/", views.story),
]
