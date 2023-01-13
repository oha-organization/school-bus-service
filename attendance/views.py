import datetime

from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import permission_required

from .models import (
    School,
    Bus,
    Student,
    StudentAttendance,
    Attendance,
    Grade,
    Destination,
)


def home(request):
    return render(request, "attendance/home.html")


@login_required
def attendance_select(request):
    bus_list = Bus.objects.filter(school=request.user.school)
    context = {"bus_list": bus_list, "today": datetime.date.today()}
    return render(request, "attendance/attendance_select.html", context)


@login_required
def attendance_display(request):
    bus = get_object_or_404(
        Bus.objects.filter(school=request.user.school), id=request.POST.get("bus")
    )
    check_date = request.POST.get("check_date")
    if request.POST["direction"] == "COMING":
        direction = "COMING"
    else:
        direction = "LEAVING"

    check_date = datetime.datetime.strptime(check_date, "%Y-%m-%d").date()
    today = datetime.date.today()

    # Get or create new attendance
    attendance, created = Attendance.objects.get_or_create(
        school=request.user.school,
        bus=bus,
        direction=direction,
        check_date=check_date,
        defaults={"teacher": request.user},
    )

    request.session["attendance_id"] = attendance.id
    request.session["bus_id"] = bus.id

    context = {
        "attendance": attendance,
    }

    if attendance.is_signed:
        studentattendance_list = StudentAttendance.objects.filter(attendance=attendance)
        context["studentattendance_list"] = studentattendance_list
        return render(request, "attendance/attendance_display_exist.html", context)
    else:
        student_list = Student.objects.filter(school=request.user.school, bus=bus)
        context["student_list"] = student_list
        return render(request, "attendance/attendance_display_new.html", context)


@login_required
def attendance_save(request):
    """Save attendance logic"""
    if request.method == "POST":
        student_list = Student.objects.filter(
            school=request.user.school, bus=request.session["bus_id"]
        )
        present_list = request.POST.getlist("present_list")

        # Delete all attendance for attendance
        attendance = get_object_or_404(
            Attendance.objects.filter(school=request.user.school),
            id=request.session.get("attendance_id"),
        )
        # Delete StudentAttendance list if already signed
        if attendance.is_signed:
            StudentAttendance.objects.filter(attendance=attendance).delete()

        # Add all student with present and absent value
        for student in student_list:
            if str(student.id) in present_list:
                StudentAttendance.objects.create(
                    attendance=attendance, student_id=student.id, present=True
                )
            else:
                StudentAttendance.objects.create(
                    attendance=attendance, student_id=student.id, present=False
                )

        # Touch Attendance Model for update to signed_at field
        attendance.is_signed = True
        attendance.teacher = request.user
        attendance.save()

        # return redirect("attendance:attendance-detail", attendance.id)
        return redirect("attendance:attendance-save-done")


@login_required
def attendance_save_done(request):
    attendance = get_object_or_404(
        Attendance.objects.filter(school=request.user.school),
        id=request.session.get("attendance_id"),
    )
    del request.session["attendance_id"]
    context = {"attendance": attendance}
    return render(request, "attendance/attendance_save_done.html", context)


@login_required
def attendance_detail(request, attendance_id):
    attendance = get_object_or_404(
        Attendance.objects.filter(school=request.user.school), id=attendance_id
    )
    context = {"attendance": attendance}
    return render(request, "attendance/attendance_detail.html", context)


@login_required
def attendance_list_view(request):
    attendance_list = Attendance.objects.filter(school=request.user.school)
    context = {
        "attendance_list": attendance_list,
    }
    return render(request, "attendance/attendance_list.html", context)


@login_required
def attendance_change(request, attendance_id):
    attendance = get_object_or_404(
        Attendance.objects.filter(school=request.user.school), id=attendance_id
    )
    studentattendance_list = StudentAttendance.objects.filter(attendance=attendance)

    request.session["attendance_id"] = attendance.id
    context = {
        "studentattendance_list": studentattendance_list,
        "attendance": attendance,
    }
    return render(request, "attendance/attendance_change.html", context)


@login_required
def attendance_delete(request, attendance_id):
    attendance = get_object_or_404(
        Attendance.objects.filter(school=request.user.school), id=attendance_id
    )

    attendance.delete()

    # return redirect("attendance:attendance-detail", attendance.id)
    return redirect("attendance:attendance-list")


@login_required
def grade_list_view(request):
    grade_list = Grade.objects.filter(school=request.user.school)
    context = {
        "grade_list": grade_list,
    }
    return render(request, "attendance/grade_list.html", context)


@login_required
def grade_add(request):
    if request.method == "POST":
        school = request.user.school
        level = request.POST["level"]
        branch = request.POST["branch"]

        grade = Grade(school=school, level=level, branch=branch)
        try:
            grade.save()
        except Exception as e:
            raise Http404("Error is: ", e)

        return redirect("attendance:home")

    return render(request, "attendance/grade_add.html")


@login_required
def grade_change(request, grade_id):
    grade = get_object_or_404(
        Grade.objects.filter(school=request.user.school), id=grade_id
    )

    if request.method == "POST":
        level = request.POST["level"]
        branch = request.POST["branch"]

        grade.level = level
        grade.branch = branch
        try:
            grade.save()
        except Exception as e:
            raise Http404("Update error.")

        return redirect("attendance:grade-list")

    context = {"grade": grade}
    return render(request, "attendance/grade_change.html", context)


@login_required
def driver_add(request):
    if request.method == "POST":
        try:
            get_user_model().objects.create_user(
                school=request.user.school,
                role="DRIVER",
                username=request.POST["username"],
                first_name=request.POST["first_name"],
                last_name=request.POST["last_name"],
                email=request.POST["email"],
                password=request.POST["password"],
            )
        except Exception as e:
            raise Http404("User creation error.")

        return redirect("attendance:driver-list")

    return render(request, "attendance/driver_add.html")


@login_required
def driver_list_view(request):
    driver_list = get_user_model().objects.filter(
        school=request.user.school, role="DRIVER"
    )
    context = {
        "driver_list": driver_list,
    }
    return render(request, "attendance/driver_list.html", context)


@login_required
def teacher_list_view(request):
    teacher_list = get_user_model().objects.filter(
        school=request.user.school, role="TEACHER"
    )
    context = {
        "teacher_list": teacher_list,
    }
    return render(request, "attendance/teacher_list.html", context)


@login_required
def teacher_add(request):
    if request.method == "POST":
        school = request.user.school
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            get_user_model().objects.create_user(
                school=school,
                role="TEACHER",
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )
        except Exception as e:
            raise Http404("User creation error.")

        return redirect("attendance:teacher-list")

    return render(request, "attendance/teacher_add.html")


@login_required
def teacher_change(request, teacher_id):
    teacher = get_object_or_404(
        get_user_model().objects.filter(school=request.user.school), id=teacher_id
    )

    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]

        teacher.username = username
        teacher.first_name = first_name
        teacher.last_name = last_name
        teacher.email = email

        try:
            teacher.save()
        except Exception as e:
            raise Http404("Teacher update error.")

        return redirect("attendance:teacher-list")

    context = {
        "teacher": teacher,
    }
    return render(request, "attendance/teacher_change.html", context)


@login_required
def teacher_change_password(request, teacher_id):
    # There must be admin or teacher themselves check
    teacher = get_object_or_404(
        get_user_model().objects.filter(school=request.user.school), id=teacher_id
    )
    context = {
        "teacher": teacher,
    }

    if request.method == "POST":
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 == password2:
            teacher.set_password(password1)
            try:
                teacher.save()
            except Exception as e:
                raise Http404("Teacher password update error.")

            return redirect("attendance:teacher-list")

        context["error_message"] = "Password does not match!"

    return render(request, "attendance/teacher_change_password.html", context)


@login_required
def bus_list_view(request):
    bus_list = Bus.objects.filter(school=request.user.school)
    context = {
        "bus_list": bus_list,
    }
    return render(request, "attendance/bus_list.html", context)


def bus_add(request):
    driver_list = get_user_model().objects.filter(
        school=request.user.school, role="DRIVER"
    )
    destination_list = Destination.objects.filter(school=request.user.school)

    if request.method == "POST":
        school = request.user.school
        driver = request.POST["driver"]
        bus_number = request.POST["bus_number"]
        capacity = request.POST["capacity"]
        plate = request.POST["plate"]
        destinations = request.POST.getlist("destinations")

        bus = Bus(
            school=school,
            driver_id=driver,
            bus_number=bus_number,
            capacity=capacity,
            plate=plate,
        )
        try:
            bus.save()
            bus.destinations.set(destinations)
        except Exception as e:
            raise Http404("Error is: ", e)

        return redirect("attendance:bus-detail", bus.id)

    context = {"driver_list": driver_list, "destination_list": destination_list}
    return render(request, "attendance/bus_add.html", context)


@login_required
def bus_detail(request, bus_id):
    bus = get_object_or_404(Bus.objects.filter(school=request.user.school), id=bus_id)
    context = {"bus": bus}
    return render(request, "attendance/bus_detail.html", context)


@login_required
def bus_change(request, bus_id):
    bus = get_object_or_404(Bus.objects.filter(school=request.user.school), id=bus_id)
    driver_list = get_user_model().objects.filter(
        school=request.user.school, role="DRIVER"
    )
    destination_list = Destination.objects.filter(school=request.user.school)

    if request.method == "POST":
        driver = request.POST["driver"]
        bus_number = request.POST["bus_number"]
        capacity = request.POST["capacity"]
        plate = request.POST["plate"]
        destinations = request.POST.getlist("destinations")

        bus.driver_id = driver
        bus.bus_number = bus_number
        bus.capacity = capacity
        bus.plate = plate
        bus.destinations.set(destinations)
        try:
            bus.save()
        except Exception as e:
            raise Http404("Update error.")

        return redirect("attendance:bus-list")

    context = {
        "bus": bus,
        "driver_list": driver_list,
        "destination_list": destination_list,
    }
    return render(request, "attendance/bus_change.html", context)


def destination_list_view(request):
    destination_list = Destination.objects.filter(school=request.user.school)
    context = {
        "destination_list": destination_list,
    }
    return render(request, "attendance/destination_list.html", context)


def destination_add(request):
    if request.method == "POST":
        school = request.user.school
        name = request.POST["name"]

        destination = Destination(school=school, name=name)
        try:
            destination.save()
        except Exception as e:
            raise Http404("Error is: ", e)

        return redirect("attendance:home")

    return render(request, "attendance/destination_add.html")


def user_role_check(user):
    # check if the user has the correct roles
    return user.role == "ADMIN" or user.role == "MANAGER"


@login_required
@user_passes_test(user_role_check)
def destination_detail(request, destination_id):
    destination = get_object_or_404(
        Destination.objects.filter(school=request.user.school), id=destination_id
    )
    context = {
        "destination": destination,
    }
    return render(request, "attendance/destination_detail.html", context)


@login_required
@user_passes_test(user_role_check)
def destination_change(request, destination_id):
    destination = get_object_or_404(
        Destination.objects.filter(school=request.user.school), id=destination_id
    )
    if request.method == "POST":
        name = request.POST["name"]
        destination.name = name
        try:
            destination.save()
        except Exception as e:
            raise Http404("Update error.")

        return redirect("attendance:destination-list")

    context = {
        "destination": destination,
    }
    return render(request, "attendance/destination_change.html", context)


def student_list_view(request):
    student_list = Student.objects.filter(school=request.user.school)
    context = {
        "student_list": student_list,
    }
    return render(request, "attendance/student_list.html", context)


@login_required
@user_passes_test(user_role_check)
def student_add(request):
    if request.method == "POST":
        school = request.user.school
        bus = request.POST["bus"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        grade = request.POST["grade"]

        student = Student(
            school=school,
            bus_id=bus,
            first_name=first_name,
            last_name=last_name,
            grade_id=grade,
        )
        try:
            student.save()
        except Exception as e:
            raise Http404("Error is: ", e)

        return redirect("attendance:home")

    bus_list = Bus.objects.filter(school=request.user.school)
    grade_list = Grade.objects.filter(school=request.user.school)

    context = {
        "bus_list": bus_list,
        "grade_list": grade_list,
    }
    return render(request, "attendance/student_add.html", context)


def student_detail(request, student_id):
    student = get_object_or_404(
        Student.objects.filter(school=request.user.school), id=student_id
    )
    context = {
        "student": student,
    }
    return render(request, "attendance/student_detail.html", context)


def student_change(request, student_id):
    student = get_object_or_404(
        Student.objects.filter(school=request.user.school), id=student_id
    )

    if request.method == "POST":
        bus = request.POST["bus"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        grade = request.POST["grade"]

        student.bus_id = bus
        student.first_name = first_name
        student.last_name = last_name
        student.grade_id = grade
        try:
            student.save()
        except Exception as e:
            raise Http404("Update Error.", e)

        return redirect("attendance:student-detail", student.id)

    bus_list = Bus.objects.filter(school=request.user.school)
    grade_list = Grade.objects.filter(school=request.user.school)

    context = {
        "student": student,
        "bus_list": bus_list,
        "grade_list": grade_list,
    }
    return render(request, "attendance/student_change.html", context)
