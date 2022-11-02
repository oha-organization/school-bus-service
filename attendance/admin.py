from django.contrib import admin

from .models import (
    School,
    Bus,
    Village,
    Grade,
    Student,
    Attendance,
    City,
    District,
    Signature,
)

admin.site.register(School)
admin.site.register(Bus)
admin.site.register(Village)
admin.site.register(Grade)
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(City)
admin.site.register(District)
admin.site.register(Signature)
