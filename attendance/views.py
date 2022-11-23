import datetime

import django.db.utils
from django.core import serializers
from django.http import Http404
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.urls import reverse

from accounts.models import User
from .models import School, Bus, Student, Attendance, Signature, Grade


def home(request):
    return render(request, "attendance/home.html")


def attendance_select(request):
    bus_list = Bus.objects.filter(school=request.user.school)
    context = {"bus_list": bus_list, "today": datetime.date.today()}
    return render(request, "attendance/attendance_select.html", context)


def attendance_get_or_create(request):
    bus = get_object_or_404(Bus.objects.all(), id=request.POST.get("bus"))
    check_date = request.POST.get("check_date")
    if request.POST["direction"] in ["COMING", "LEAVING"]:
        direction = request.POST["direction"]
    else:
        raise ValueError("Don't tamper post direction data!")

    student_list = Student.objects.filter(bus=bus)

    # Get or create new signature
    signature, created = Signature.objects.get_or_create(
        school=request.user.school,
        bus=bus,
        direction=direction,
        check_date=check_date,
        defaults={"teacher": request.user},
    )

    request.session["signature_id"] = signature.id
    request.session["bus_id"] = bus.id

    # If signature is already exist get unattended student list
    student_already_absent_list = []
    if not created:
        student_already_absent_list = Student.objects.filter(
            attendance__signature=signature
        )

    context = {
        "student_list": student_list,
        "student_already_absent_list": student_already_absent_list,
        "signature": signature,
    }
    return render(request, "attendance/attendance_get_or_create.html", context)


def attendance_save(request):
    """Save attendance logic"""
    if request.method == "POST":
        # For security reason check absent_students are in bus student_list
        student_list = Student.objects.filter(bus=request.session["bus_id"])
        student_list = [str(student.id) for student in student_list]
        student_absent_list = request.POST.getlist("student_absent_list")

        check_all_absent_student_in_student_list = all(item in student_list for item in student_absent_list)
        if not check_all_absent_student_in_student_list:
            raise Http404("TAMPERED STUDENT DATA...")

        # Delete all attendance for signature
        signature = Signature.objects.get(id=request.session["signature_id"])
        Attendance.objects.filter(signature=signature).delete()

        # Add absent students to Attendance
        for student in student_absent_list:
            Attendance.objects.create(signature=signature, student_id=student)

        # Touch Signature Model for update to signed_at field
        signature.is_signed = True
        signature.save()

        # return redirect("attendance:signature-detail", signature.id)
        return redirect("attendance:attendance-save-done")


def attendance_save_done(request):
    signature = get_object_or_404(
        Signature.objects.all(), id=request.session.get("signature_id")
    )
    del request.session["signature_id"]
    context = {"signature": signature}
    return render(request, "attendance/attendance_save_done.html", context)


def signature_detail(request, signature_id):
    signature = get_object_or_404(Signature.objects.all(), id=signature_id)
    context = {"signature": signature}
    return render(request, "attendance/signature_detail.html", context)


def grade_add(request):
    if request.method == "POST":
        school = request.user.school
        level = request.POST["level"]
        branch = request.POST["branch"]

        grade = Grade(school=school, level=level, branch=branch)
        try:
            grade.save()
        except Exception as e:
            print("Error is: ", e)
            raise Http404("The Grade has already exist.")

        return redirect("attendance:home")

    return render(request, "attendance/grade_add.html")


def grade_list_view(request):
    grade_list = Grade.objects.filter(school=request.user.school)
    context = {"grade_list": grade_list,}
    return render(request, "attendance/grade_list.html", context)


def grade_change(request, grade_id):
    grade = get_object_or_404(Grade.objects.filter(school=request.user.school), id=grade_id)

    if request.method == "POST":
        level = request.POST["level"]
        branch = request.POST["branch"]

        # If nothing change doesn't touch database
        if not (grade.level == level and grade.branch == branch):
            grade.level = level
            grade.branch = branch
            try:
                grade.save()
            except Exception as e:
                raise Http404("Update error.")

        return redirect("attendance:grade-list")

    context = {"grade": grade}
    return render(request, "attendance/grade_change.html", context)
