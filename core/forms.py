from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import MedicalRecord, Prescription, Allergy
from django.utils import timezone
from .models import *  # Importe tous les modèles depuis models.py


class UserRegistrationForm(UserCreationForm):
    """
    Formulaire d'inscription personnalisé étendant UserCreationForm
    Ajoute des champs spécifiques pour notre application médicale
    """

    # Définition des rôles disponibles à l'inscription
    ROLE_CHOICES = [
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Médecin'),
    ]

    # Champ personnalisé pour le rôle (obligatoire)
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    # Champ email obligatoire (plus important que le username)
    email = forms.EmailField(required=True)

    class Meta:
        model = User  # Utilise notre modèle User personnalisé
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    """
    Formulaire de connexion personnalisé étendant AuthenticationForm
    """

    # Personnalisation du champ username
    username = forms.CharField(label="Email/Nom d'utilisateur")
    # Ajout d'une case à cocher "Se souvenir de moi"
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput())


class AppointmentForm(forms.ModelForm):
    """
    Formulaire pour la création/modification de rendez-vous
    """

    class Meta:
        model = Appointment  # Utilise le modèle Appointment
        fields = ['doctor', 'date_time', 'appointment_type', 'notes']
        widgets = {
            # Utilise un input datetime-local pour une meilleure expérience utilisateur
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class PatientForm(forms.ModelForm):
    """
    Formulaire pour les informations spécifiques aux patients
    """

    class Meta:
        model = Patient  # Utilise le modèle Patient
        fields = ['birth_date', 'blood_group', 'medical_history']
        widgets = {
            # Input de type date pour la date de naissance
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class DoctorForm(forms.ModelForm):
    """
    Formulaire pour les informations spécifiques aux médecins
    """

    class Meta:
        model = Doctor  # Utilise le modèle Doctor
        fields = ['speciality', 'license_number', 'availability']


class MedicalRecordForm(forms.ModelForm):
    """
    Formulaire pour la création/modification de dossiers médicaux
    Contrôle strict sur les dates possibles
    """

    class Meta:
        model = MedicalRecord  # Utilise le modèle MedicalRecord
        fields = ['record_type', 'title', 'description', 'date', 'file', 'is_emergency', 'confidential']
        widgets = {
            # Limite la date maximale à aujourd'hui
            'date': forms.DateInput(attrs={
                'type': 'date',
                'max': timezone.now().date()  # Empêche de sélectionner une date future
            }),
            # Zone de texte plus grande pour la description
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class PrescriptionForm(forms.ModelForm):
    """
    Formulaire pour la création d'ordonnances
    Inclut une validation personnalisée pour les médicaments
    """

    class Meta:
        model = Prescription  # Utilise le modèle Prescription
        fields = ['medications', 'instructions', 'valid_until']
        widgets = {
            # Input de type date pour la validité
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            # Zone de texte pour les instructions
            'instructions': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_medications(self):
        """
        Validation personnalisée pour le champ medications (format JSON)
        """
        medications = self.cleaned_data.get('medications')
        # Ici vous pourriez ajouter une validation du format JSON
        # Par exemple vérifier que chaque médicament a bien un nom et un dosage
        return medications


class AllergyForm(forms.ModelForm):
    """
    Formulaire pour la gestion des allergies des patients
    """

    class Meta:
        model = Allergy  # Utilise le modèle Allergy
        fields = ['name', 'severity', 'reaction', 'onset_date', 'active']
        widgets = {
            # Input de type date pour la date d'apparition
            'onset_date': forms.DateInput(attrs={'type': 'date'}),
            # Zone de texte pour décrire la réaction
            'reaction': forms.Textarea(attrs={'rows': 3}),
        }