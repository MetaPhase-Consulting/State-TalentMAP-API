from django.http import HttpResponse


def devIndex(request):
    return HttpResponse("Hello, world. You're at the development index.")