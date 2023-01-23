from django.contrib import admin

from .models import (
    School,
    Bus,
    Grade,
    Student,
    Attendance,
    Destination,
    StudentAttendance,
)

admin.site.register(School)
admin.site.register(Bus)
admin.site.register(Grade)
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Destination)
admin.site.register(StudentAttendance)
