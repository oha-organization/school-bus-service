from django.urls import path
from . import views


app_name = "attendance"
urlpatterns = [
    path("", views.home, name="home"),
    path("select/", views.attendance_select, name="attendance-select"),
    path("display/", views.attendance_get_or_create, name="attendance-get-or-create"),
    path("save/", views.attendance_save, name="attendance-save"),
    path("save-done/", views.attendance_save_done, name="attendance-save-done"),
    path(
        "signature/<int:signature_id>/", views.signature_detail, name="signature-detail"
    ),
    path("grade/", views.grade_list_view, name="grade-list"),
    path("grade/add/", views.grade_add, name="grade-add"),
    path("grade/<int:grade_id>/change/", views.grade_change, name="grade-change"),
    path("teacher/", views.teacher_list_view, name="teacher-list"),
    path("driver/", views.driver_list_view, name="driver-list"),
    path("teacher/add/", views.teacher_add, name="teacher-add"),
    path(
        "teacher/<int:teacher_id>/change/", views.teacher_change, name="teacher-change"
    ),
    path(
        "teacher/<int:teacher_id>/password/", views.teacher_change_password, name="teacher-change-password"
    ),
]
