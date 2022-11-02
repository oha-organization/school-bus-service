import datetime

from django.core import serializers
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.urls import reverse

from accounts.models import User
from .models import School, Bus, Student, Attendance, Signature


def home(request):
    return render(request, "attendance/home.html")


def attendance_choose(request):
    bus_list = Bus.objects.filter(school=request.user.school)
    context = {"bus_list": bus_list, "today": datetime.date.today()}
    return render(request, "attendance/attendance_choose.html", context)


def attendance_display(request):
    bus = get_object_or_404(Bus.objects.all(), id=request.POST.get("bus"))
    check_date = request.POST.get("check_date")
    if request.POST.get("direction") in ["COMING", "LEAVING"]:
        direction = request.POST.get("direction")
    else:
        raise ValueError("Don't tamper post data!")

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
    return render(request, "attendance/attendance_display.html", context)


def attendance_save(request):
    """Save attendance logic"""
    if request.method == "POST":
        student_absent_list = request.POST.getlist("student_absent_list")

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
        Signature.objects.all(), id=request.session["signature_id"]
    )
    context = {"signature": signature}
    return render(request, "attendance/attendance_save_done.html", context)


def signature_detail(request, signature_id):
    signature = get_object_or_404(Signature.objects.all(), id=signature_id)
    context = {"signature": signature}
    return render(request, "attendance/signature_detail.html", context)
