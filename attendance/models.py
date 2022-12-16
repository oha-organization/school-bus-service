from django.db import models
from django.conf import settings


class School(models.Model):
    name = models.CharField(max_length=255)
    code = models.IntegerField()

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse("attendance:school-detail", kwargs={"pk": self.pk})


class Destination(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Bus(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    # https://docs.djangoproject.com/en/4.1/ref/models/fields/#django.db.models.ForeignKey.limit_choices_to
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        limit_choices_to={"role": "DRIVER"},
        blank=True,
        null=True,
    )
    bus_number = models.CharField(max_length=255)
    capacity = models.IntegerField()
    plate = models.CharField(max_length=11)
    destinations = models.ManyToManyField(Destination)

    class Meta:
        verbose_name_plural = "busses"

    def __str__(self):
        return self.bus_number


class Grade(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    level = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)

    class Meta:
        ordering = ["level"]
        constraints = [
            models.UniqueConstraint(
                fields=["level", "branch"],
                name="unique_grade_level_and_branch",
            )
        ]

    def __str__(self):
        return f"{self.level}/{self.branch}"


class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)

    class Meta:
        ordering = ["first_name"]

    def __str__(self):
        return f"{self.first_name}  {self.last_name}"


class Attendance(models.Model):
    DIRECTION_CHOICES = (
        ("COMING", "COMING"),
        ("LEAVING", "LEAVING"),
    )
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    check_date = models.DateField()
    direction = models.CharField(max_length=7, choices=DIRECTION_CHOICES)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    signed_at = models.DateTimeField(auto_now=True)
    is_signed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-check_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "bus", "check_date", "direction"],
                name="unique_attendance_with_school_bus_date_and_direction",
            )
        ]

    def __str__(self):
        return (
            f"{self.school.name} | {self.bus} | {self.check_date} | {self.direction} | "
            f"{self.teacher} | {self.is_signed}"
        )

    # def get_absolute_url(self):
    #     return reverse("attendance-detail", kwargs={"pk": self.pk})


class StudentAttendance(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    present = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        ordering = ["-attendance"]

        constraints = [
            models.UniqueConstraint(
                fields=["attendance", "student"],
                name="unique_student_with_student_and_attendance",
            )
        ]

    def __str__(self):
        return f"{self.attendance.id} | {self.student} | {self.present}"
