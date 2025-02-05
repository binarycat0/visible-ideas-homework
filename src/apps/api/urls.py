from django.urls import path
from . import views
urlpatterns = [
    path("crawler", views.CrawlerApi.as_view({"get": "get"})),
]