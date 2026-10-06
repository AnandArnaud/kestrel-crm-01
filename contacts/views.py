from django.http import HttpRequest, JsonResponse
from django.template.response import TemplateResponse

from .models import Contact


def health(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"ok": True})


def contact_list(request: HttpRequest) -> TemplateResponse:
    return TemplateResponse(request, "contacts/list.html", {"contacts": Contact.objects.all()})


def contact_list_json(request: HttpRequest) -> JsonResponse:
    contacts = list(Contact.objects.values("id", "name", "email", "company", "created_at"))
    return JsonResponse({"contacts": contacts})
