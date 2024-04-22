from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    HomePageView,
    AboutPageView,
    ProfilePageView,
    cancel_request,
    manage_requests,
)
from pages import views

urlpatterns = [
    path("", views.home, name="home"),
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("profile/", ProfilePageView.as_view(), name="profile"),
    path("request/", views.submit_request, name="submit_request"),
    path("cancel_request/<int:request_id>/", cancel_request, name="cancel_request"),
    path("manage-requests/", manage_requests, name="manage_requests"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
