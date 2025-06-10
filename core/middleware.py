from django.shortcuts import redirect
from django.urls import reverse
from django.utils.timezone import now

class SuspensionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            # проверяем активные блокировки
            active = user.suspensions.filter(start__lte=now(), end__gt=now()).exists()
            if active:
                # если уже на странице уведомления — не редиректить в цикл
                if request.path != reverse("suspended"):
                    return redirect("suspended")
        return self.get_response(request)