from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

# Custom User Model
class User(AbstractUser):
    USER_TYPE_CHOICES = (("faculty", "Faculty"), ("student", "Student"))

    username = None  # Remove username
    email = models.EmailField(unique=True)  # Use email for login
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default="faculty")

    groups = models.ManyToManyField(Group, blank=True)
    user_permissions = models.ManyToManyField(Permission, blank=True)

    objects = CustomUserManager()  

    USERNAME_FIELD = "email"  # Login using email
    REQUIRED_FIELDS = ["first_name", "last_name"]  

    def __str__(self):
        return self.email

# Batch Model (Admission Year)
class Batch(models.Model):
    year = models.IntegerField(unique=True)  # Example: 2025, 2026

    def __str__(self):
        return str(self.year)

class Branch(models.Model):
    name = models.CharField(max_length=100)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="branches", default=1)

    class Meta:
        unique_together = ('name', 'batch')

    def __str__(self):
        return f"{self.name} ({self.batch.year})"

class Year(models.Model):
    YEAR_CHOICES = [
        (1, "1st Year"), 
        (2, "2nd Year"), 
        (3, "3rd Year"), 
        (4, "4th Year")
    ]

    year = models.PositiveIntegerField(choices=YEAR_CHOICES)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="years")
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="years", default=1)

    class Meta:
        unique_together = ("year", "branch", "batch")

    def __str__(self):
        return f"{dict(self.YEAR_CHOICES).get(self.year, 'Unknown Year')} - {self.branch.name} - {self.batch.year}"

class Semester(models.Model):
    SEMESTER_CHOICES = [(1, "Semester 1"), (2, "Semester 2")]

    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name="semesters")
    sem_number = models.PositiveIntegerField(choices=SEMESTER_CHOICES, default=1)

    class Meta:
        unique_together = ("year", "sem_number")

    def __str__(self):
        return f"Semester {self.sem_number} ({self.year})"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name="subjects")
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="subjects")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="subjects")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="subjects")

    class Meta:
        unique_together = ("name", "year", "batch", "branch", "semester")

    def __str__(self):
        return f"{self.name} ({self.branch.name} - {self.year.year} - Semester {self.semester.sem_number})"

# Faculty Model 
class Faculty(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="faculty")
    batches = models.ManyToManyField(Batch, blank=True, related_name="faculty_batches")
    branches = models.ManyToManyField(Branch, blank=True, related_name="faculty_branches")
    years = models.ManyToManyField(Year, blank=True, related_name="faculty_years")
    semesters = models.ManyToManyField(Semester, blank=True, related_name="faculty_semesters")
    subjects = models.ManyToManyField(Subject, blank=True, related_name="faculty_members")

    def clean(self):
        if self.user.user_type != "faculty":
            raise ValidationError("Faculty must have user_type='faculty'")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.email

# Student Model
class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student")
    roll_number = models.CharField(max_length=20, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="students")
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="students")

    def clean(self):
        if self.user.user_type != "student":
            raise ValidationError("Student must have user_type='student'")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} ({self.branch.name} - Batch {self.batch.year})"

# Note Model 
class Note(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="notes/")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="notes")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.subject.name})"