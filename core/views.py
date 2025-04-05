from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import MedicalRecord, Prescription, Allergy
from .models import *  # Importe tous les modèles
from .forms import *  # Importe tous les formulaires

def home(request):
    """Vue pour la page d'accueil non authentifiée"""
    return render(request, 'home.html')

@login_required
@login_required
def dashboard(request):
    """Tableau de bord personnalisé selon le rôle"""
    context = {}

    try:
        if request.user.role == 'PATIENT':
            # Vérifie si le profil patient existe, sinon le crée
            patient_profile, created = Patient.objects.get_or_create(user=request.user)
            appointments = Appointment.objects.filter(patient=patient_profile)
            context['appointments'] = appointments[:5]

        elif request.user.role == 'DOCTOR':
            # Vérifie si le profil docteur existe
            if hasattr(request.user, 'doctor_profile'):
                appointments = Appointment.objects.filter(doctor=request.user.doctor_profile)
                context['appointments'] = appointments[:5]
            else:
                messages.warning(request, "Votre profil médecin n'est pas complètement configuré")

        elif request.user.role == 'ADMIN':
            context['doctor_count'] = Doctor.objects.count()
            context['patient_count'] = Patient.objects.count()
            context['appointment_count'] = Appointment.objects.count()

    except Exception as e:
        messages.error(request, f"Une erreur est survenue: {str(e)}")
        logger.error(f"Dashboard error for user {request.user.id}: {str(e)}")

    return render(request, 'dashboard.html', context)

class DoctorListView(ListView):
    """Affiche la liste des médecins (accès public)"""
    model = Doctor
    template_name = 'doctors/list.html'
    context_object_name = 'doctors'  # Nom de la variable dans le template

class DoctorDetailView(DetailView):
    """Affiche le détail d'un médecin (accès public)"""
    model = Doctor
    template_name = 'doctors/detail.html'

class PatientListView(ListView):
    """Affiche la liste des patients (accès restreint)"""
    model = Patient
    template_name = 'patients/list.html'
    context_object_name = 'patients'

class AppointmentCreateView(CreateView):
    """Permet de créer un nouveau rendez-vous"""
    model = Appointment
    form_class = AppointmentForm  # Formulaire personnalisé
    template_name = 'appointments/create.html'
    success_url = reverse_lazy('appointment_list')  # Redirection après succès

    def form_valid(self, form):
        """Si c'est un patient qui crée le RDV, on l'associe automatiquement"""
        if self.request.user.role == 'PATIENT':
            form.instance.patient = self.request.user.patient_profile
        return super().form_valid(form)

def register(request):
    """Gère l'inscription des nouveaux utilisateurs"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Crée le nouvel utilisateur
            login(request, user)  # Connecte automatiquement
            messages.success(request, "Inscription réussie !")
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()

    return render(request, 'auth/register.html', {'form': form})

def user_login(request):
    """Gère la connexion des utilisateurs existants"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue {user.username} !")
                return redirect('dashboard')
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form})

@login_required
def user_logout(request):
    """Déconnecte l'utilisateur"""
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('home')

class MedicalRecordListView(LoginRequiredMixin, ListView):
    """
    Affiche la liste des dossiers médicaux
    - Patients: voient leurs propres dossiers
    - Médecins: voient les dossiers de leurs patients
    """
    model = MedicalRecord
    template_name = 'medical_records/list.html'
    context_object_name = 'records'

    def get_queryset(self):
        """Filtre les résultats selon le rôle"""
        queryset = super().get_queryset()
        if self.request.user.role == 'PATIENT':
            return queryset.filter(patient=self.request.user.patient_profile)
        elif self.request.user.role == 'DOCTOR':
            return queryset.filter(patient__in=self.request.user.doctor_profile.patients.all())
        return queryset.none()  # Retourne aucun résultat par défaut

class MedicalRecordCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Permet de créer un nouveau dossier médical
    Accès réservé aux médecins et admins
    """
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'medical_records/create.html'
    success_url = reverse_lazy('medical_record_list')

    def test_func(self):
        """Vérifie que l'utilisateur a les droits nécessaires"""
        return self.request.user.role in ['DOCTOR', 'ADMIN']

    def form_valid(self, form):
        """Associe automatiquement le médecin et le patient"""
        form.instance.doctor = self.request.user.doctor_profile
        form.instance.patient_id = self.kwargs['patient_id']
        return super().form_valid(form)

class MedicalRecordDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Affiche le détail d'un dossier médical
    Contrôle d'accès personnalisé
    """
    model = MedicalRecord
    template_name = 'medical_records/detail.html'
    context_object_name = 'record'

    def test_func(self):
        """Vérifie les permissions d'accès"""
        record = self.get_object()
        user = self.request.user
        if user.role == 'PATIENT':
            return record.patient == user.patient_profile
        elif user.role == 'DOCTOR':
            return record.patient in user.doctor_profile.patients.all()
        return user.role == 'ADMIN'

class PrescriptionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Permet de créer une ordonnance
    Accès réservé aux médecins et admins
    """
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'medical_records/prescription_create.html'

    def test_func(self):
        """Vérifie que l'utilisateur a les droits nécessaires"""
        return self.request.user.role in ['DOCTOR', 'ADMIN']

    def get_success_url(self):
        """Redirige vers le dossier médical après création"""
        return reverse_lazy('medical_record_detail', kwargs={'pk': self.object.medical_record_id})

    def get_context_data(self, **kwargs):
        """Ajoute le dossier médical au contexte"""
        context = super().get_context_data(**kwargs)
        context['medical_record'] = MedicalRecord.objects.get(pk=self.kwargs['record_id'])
        return context

    def form_valid(self, form):
        """Associe automatiquement l'ordonnance au dossier médical"""
        form.instance.medical_record_id = self.kwargs['record_id']
        return super().form_valid(form)