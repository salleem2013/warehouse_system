from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    HomePageView,
    AboutPageView,
    ProfilePageView,
    cancel_request,
    manage_requests,
    profile_view,
)
from pages import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.AboutPageView.as_view(), name="about"),
    path("profile/", views.profile_view, name="profile"),
    path("request/", views.submit_request, name="submit_request"),
    path(
        "cancel_request/<int:request_id>/", views.cancel_request, name="cancel_request"
    ),
    path("manage-requests/", views.manage_requests, name="manage_requests"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
