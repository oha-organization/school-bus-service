from django.urls import path
from . import views


app_name = "attendance"
urlpatterns = [
    path("", views.home, name="home"),
    path("select/", views.attendance_select, name="attendance-select"),
    path("display/", views.attendance_get_or_create, name="attendance-get-or-create"),
    path("save/", views.attendance_save, name="attendance-save"),
    path("save-done/", views.attendance_save_done, name="attendance-save-done"),
    path("signature/<int:signature_id>/", views.signature_detail, name="signature-detail"),
    path("grade/add/", views.grade_add, name="grade-add"),
]
