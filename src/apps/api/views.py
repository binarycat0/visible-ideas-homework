from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


# Create your views here.
class CrawlerApi(ViewSet):

    def post(self, request):
        return Response(data={"status": "ok"})

    def get(self, request):
        return Response(data={"status": "ok"})

    def list(self, request):
        return Response(data={"status": "ok"})
