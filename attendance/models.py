from django.db import models
from django.conf import settings


class City(models.Model):
    name = models.CharField(max_length=255)
    post_code = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class School(models.Model):
    name = models.CharField(max_length=255)
    code = models.IntegerField()
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, blank=True, null=True
    )
    address_detail = models.CharField(max_length=512, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse("attendance:school-detail", kwargs={"pk": self.pk})


class Village(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse("attendance:village-detail", kwargs={"pk": self.pk})


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
    village = models.ManyToManyField(Village)

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
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    village = models.ForeignKey(Village, on_delete=models.CASCADE)

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
    version = models.IntegerField(default=0, blank=True, null=True)
    check_date = models.DateField()
    direction = models.CharField(max_length=7, choices=DIRECTION_CHOICES)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    signed_at = models.DateTimeField(auto_now=True)
    is_signed = models.BooleanField(default=False)
    num_absent_student = models.PositiveIntegerField(blank=True, null=True)
    num_total_student = models.PositiveIntegerField(blank=True, null=True)

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
            f"{self.school.name} | {self.bus.bus_number} | {self.check_date} | {self.direction} | "
            f"version:{self.version} | "
            f"Absent:{self.num_absent_student} | Total:{self.num_total_student} | {self.teacher.username} | "
            f"{self.is_signed}"
        )

    # def get_absolute_url(self):
    #     return reverse("attendance-detail", kwargs={"pk": self.pk})


class AbsentStudent(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-attendance"]
        constraints = [
            models.UniqueConstraint(
                fields=["attendance", "student"],
                name="unique_absent_student_with_student_and_attendance",
            )
        ]

    def __str__(self):
        return f"{self.attendance.id} | {self.student}"


class BusMember(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(auto_now_add=True)
    finish_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # Add here meta constraint for school bus student version
    # def save(self, *args, **kwargs):
    #     # It's not working now :) new commit will be fixed
    #     print("add new bus_member_version")
    #     if BusMember.objects.filter(school=self.school, bus=self.bus, is_active=True):
    #         get_version = BusMember.objects.filter(school=self.school, bus=self.bus, is_active=True)[0]
    #         get_version.version += 1
    #         print(f"New bus_member_version is created with  id number.")
    #         print(get_version.version)
    #         self.version = get_version.version
    #     super().save(*args, **kwargs)  # Call the "real" save() method.
    #     print(
    #         "save bus member to new_bus_member_version and False old bus_member_version change all old value."
    #     )

    def __str__(self):
        return f"{self.bus}, {self.student}, {self.version}, {self.is_active}"
