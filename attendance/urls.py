from django.urls import path
from . import views


app_name = "attendance"
urlpatterns = [
    path("", views.home, name="home"),
    path("school/", views.school_list, name="school-list"),
    path("school-by-user/", views.school_by_user, name="school-by-user"),
    path(
        "attendance-choose/<int:school_id>/",
        views.attendance_choose,
        name="attendance-choose",
    ),
    path(
        "attendance-choose-by-user/",
        views.attendance_choose_by_user,
        name="attendance-choose-by-user",
    ),
    path("attendance-get/", views.attendance_get, name="attendance-get"),
    path(
        "attendance-get-by-user/",
        views.attendance_get_by_user,
        name="attendance-get-by-user",
    ),
    path("attendance-save/", views.attendance_save, name="attendance-save"),
    path(
        "attendance-save-done/", views.attendance_save_done, name="attendance-save-done"
    ),
    path(
        "signature/<int:signature_id>/", views.signature_detail, name="signature-detail"
    ),
]
