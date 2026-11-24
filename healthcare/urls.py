from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_root(request):
    return JsonResponse({
        "message": "Healthcare Backend API",
        "endpoints": {
            "auth": {
                "register": "/api/auth/register/",
                "login": "/api/auth/login/",
                "token_refresh": "/api/auth/token/refresh/",
                "me": "/api/auth/me/",
            },
            "patients": "/api/patients/",
            "doctors": "/api/doctors/",
            "mappings": "/api/mappings/",
            "admin": "/admin/",
        },
    })


urlpatterns = [
    path("", api_root),
    path("api/", api_root),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/patients/", include("patients.urls")),
    path("api/doctors/", include("doctors.urls")),
    path("api/mappings/", include("mappings.urls")),
]
