from enum import StrEnum

from django.core.handlers.wsgi import WSGIRequest
from django.views.generic import TemplateView

from .exceptions import ServiceException
from .services import crawler_service


class Status(StrEnum):
    OK = "OK"
    ERROR = "ERROR"


class Index(TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request: WSGIRequest, *args, **kwargs):
        url = request.POST.get("url")

        context = self.get_context_data(**kwargs)
        context["url"] = url

        status = Status.OK

        try:
            result = crawler_service.get_external_links(url)
            context['result'] = result
        except ServiceException as ex:
            status = Status.ERROR
            context["error"] = str(ex)

        context["status"] = status
        return self.render_to_response(context)
