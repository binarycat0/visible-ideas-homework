from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.
class Index(TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
