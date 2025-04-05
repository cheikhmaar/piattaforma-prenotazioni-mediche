from django.urls import path
from . import views
from .views import (MedicalRecordListView, MedicalRecordCreateView,
                    MedicalRecordDetailView, PrescriptionCreateView)

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Authentification
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Médecins
    path('doctors/', views.DoctorListView.as_view(), name='doctor_list'),
    path('doctors/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),

    # Patients
    path('patients/', views.PatientListView.as_view(), name='patient_list'),

    # Rendez-vous
    #path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/new/', views.AppointmentCreateView.as_view(), name='appointment_create'),

    # Dossiers médicaux
    path('patients/<int:patient_id>/records/', MedicalRecordListView.as_view(), name='medical_record_list'),
    path('patients/<int:patient_id>/records/new/', MedicalRecordCreateView.as_view(), name='medical_record_create'),
    path('records/<int:pk>/', MedicalRecordDetailView.as_view(), name='medical_record_detail'),

    # Ordonnances
    path('records/<int:record_id>/prescription/', PrescriptionCreateView.as_view(), name='prescription_create'),

    # URLs pour la réinitialisation de mot de passe
    #path('password_reset/',auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html'),
     #    name='password_reset'),
]
