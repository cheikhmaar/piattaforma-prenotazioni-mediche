from rest_framework.permissions import BasePermission


class IsDoctorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['DOCTOR', 'ADMIN']


class IsPatientOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.patient.user == request.user


class IsDoctorForPatient(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.doctor_profile.patients.filter(id=obj.patient.id).exists()