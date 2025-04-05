from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


# Modèle utilisateur personnalisé héritant de AbstractUser
class User(AbstractUser):
    """
    Modèle utilisateur personnalisé qui étend AbstractUser.
    Ajoute des champs spécifiques pour les rôles et informations supplémentaires.
    """

    # Choix possibles pour le rôle de l'utilisateur
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('DOCTOR', 'Médecin'),
        ('PATIENT', 'Patient'),
    ]

    # Champ pour le rôle avec 'Patient' comme valeur par défaut
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PATIENT')
    # Numéro de téléphone (optionnel)
    phone = models.CharField(max_length=20, blank=True)
    # Adresse (optionnelle)
    address = models.TextField(blank=True)

    class Meta:
        verbose_name = _('user')  # Nom singulier dans l'admin
        verbose_name_plural = _('users')  # Nom pluriel dans l'admin


# Modèle pour les spécialités médicales
class Speciality(models.Model):
    """
    Représente une spécialité médicale (ex: Cardiologie, Pédiatrie)
    """
    name = models.CharField(max_length=100)  # Nom de la spécialité
    description = models.TextField(blank=True)  # Description détaillée

    def __str__(self):
        return self.name  # Représentation textuelle


# Modèle pour les médecins
class Doctor(models.Model):
    """
    Profil étendu pour les médecins, lié à un utilisateur
    """
    # Relation one-to-one avec le modèle User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    # Spécialité du médecin (peut être null)
    speciality = models.ForeignKey(Speciality, on_delete=models.SET_NULL, null=True)
    # Numéro de licence professionnelle
    license_number = models.CharField(max_length=50)
    # Disponibilités stockées en JSON (ex: {"Lundi": ["09:00", "10:00"]})
    availability = models.JSONField(default=dict)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"  # Représentation textuelle


# Modèle pour les patients
class Patient(models.Model):
    """
    Profil étendu pour les patients, lié à un utilisateur
    """
    # Groupes sanguins possibles
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    # Relation one-to-one avec le modèle User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    # Date de naissance du patient
    birth_date = models.DateField()
    # Groupe sanguin parmi les choix définis
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    # Historique médical (optionnel)
    medical_history = models.TextField(blank=True)

    def __str__(self):
        return self.user.get_full_name()  # Représentation textuelle


# Modèle pour les rendez-vous
class Appointment(models.Model):
    """
    Représente un rendez-vous entre un patient et un médecin
    """
    # Statuts possibles d'un rendez-vous
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('CONFIRMED', 'Confirmé'),
        ('CANCELLED', 'Annulé'),
        ('COMPLETED', 'Terminé'),
    ]

    # Types de consultation possibles
    TYPE_CHOICES = [
        ('IN_PERSON', 'Présentiel'),
        ('REMOTE', 'Téléconsultation'),
    ]

    # Patient associé au rendez-vous
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    # Médecin associé au rendez-vous
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    # Date et heure du rendez-vous
    date_time = models.DateTimeField()
    # Statut actuel du rendez-vous
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    # Type de consultation
    appointment_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    # Notes supplémentaires (optionnelles)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['date_time']  # Tri par défaut par date/heure

    def __str__(self):
        return f"RDV {self.patient} avec {self.doctor} le {self.date_time}"


# Modèle pour les pharmacies
class Pharmacy(models.Model):
    """
    Représente une pharmacie avec ses informations géographiques
    """
    name = models.CharField(max_length=100)  # Nom de la pharmacie
    address = models.TextField()  # Adresse complète
    phone = models.CharField(max_length=20)  # Numéro de téléphone
    # Indique si la pharmacie est de garde
    is_on_duty = models.BooleanField(default=False)
    latitude = models.FloatField()  # Coordonnée GPS
    longitude = models.FloatField()  # Coordonnée GPS

    def __str__(self):
        return self.name  # Représentation textuelle


# Modèle pour les dossiers médicaux
class MedicalRecord(models.Model):
    """
    Représente un dossier médical lié à un patient
    """
    # Types de dossiers médicaux possibles
    RECORD_TYPES = [
        ('CONSULT', 'Consultation'),
        ('LAB', 'Résultat de laboratoire'),
        ('IMAGING', 'Imagerie médicale'),
        ('PRESCRIPTION', 'Ordonnance'),
        ('OTHER', 'Autre'),
    ]

    # Patient associé au dossier
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='medical_records')
    # Médecin associé (peut être null)
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    # Type de dossier médical
    record_type = models.CharField(max_length=12, choices=RECORD_TYPES)
    # Titre du dossier
    title = models.CharField(max_length=200)
    # Description détaillée
    description = models.TextField()
    # Date du dossier (par défaut aujourd'hui)
    date = models.DateField(default=timezone.now)
    # Fichier associé (scans, résultats, etc.)
    file = models.FileField(upload_to='medical_records/%Y/%m/%d/', null=True, blank=True)
    # Date de création (auto)
    created_at = models.DateTimeField(auto_now_add=True)
    # Date de mise à jour (auto)
    updated_at = models.DateTimeField(auto_now=True)
    # Indique si c'est une urgence
    is_emergency = models.BooleanField(default=False)
    # Indique si le dossier est confidentiel
    confidential = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date', '-created_at']  # Tri par date décroissante
        verbose_name = 'Dossier Médical'
        verbose_name_plural = 'Dossiers Médicaux'

    def __str__(self):
        return f"{self.get_record_type_display()} - {self.patient.user.get_full_name()} ({self.date})"


# Modèle pour les ordonnances
class Prescription(models.Model):
    """
    Représente une ordonnance médicale, liée à un dossier médical
    """
    # Relation one-to-one avec le dossier médical
    medical_record = models.OneToOneField(MedicalRecord, on_delete=models.CASCADE, primary_key=True)
    # Médicaments prescrits (stockés en JSON)
    medications = models.JSONField()  # Format: [{"name": "...", "dosage": "...", ...}]
    # Instructions supplémentaires
    instructions = models.TextField(blank=True)
    # Date de validité de l'ordonnance
    valid_until = models.DateField()

    def __str__(self):
        return f"Ordonnance #{self.medical_record_id}"


# Modèle pour les allergies
class Allergy(models.Model):
    """
    Représente une allergie d'un patient
    """
    # Niveaux de sévérité possibles
    SEVERITY_CHOICES = [
        ('MILD', 'Léger'),
        ('MODERATE', 'Modéré'),
        ('SEVERE', 'Sévère'),
        ('LIFE_THREATENING', 'Menace vitale'),
    ]

    # Patient associé à l'allergie
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='allergies')
    # Nom de l'allergie
    name = models.CharField(max_length=100)
    # Niveau de sévérité
    severity = models.CharField(max_length=17, choices=SEVERITY_CHOICES)
    # Réactions observées
    reaction = models.TextField()
    # Date d'apparition
    onset_date = models.DateField()
    # Indique si l'allergie est toujours active
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Allergie'
        verbose_name_plural = 'Allergies'

    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"