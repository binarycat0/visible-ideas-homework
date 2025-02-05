from django.conf import settings
from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

urlpatterns = [
    path("", cache_page(settings.CACHE_TIMEOUT)(views.Index.as_view()), name="index"),
]
