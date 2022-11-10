from django.urls import path
from . import views


app_name = "attendance"
urlpatterns = [
    path("", views.home, name="home"),
    path("choose/", views.attendance_choose, name="attendance-choose"),
    path("display/", views.attendance_display, name="attendance-display"),
    path("save/", views.attendance_save, name="attendance-save"),
    path("save-done/", views.attendance_save_done, name="attendance-save-done"),
    path("signature/<int:signature_id>/", views.signature_detail, name="signature-detail"),
]
