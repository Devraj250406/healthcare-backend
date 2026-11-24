from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models

from patients.models import phone_validator


class Doctor(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctors"
    )
    name = models.CharField(max_length=150)
    specialization = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, validators=[phone_validator])
    years_of_experience = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(70)]
    )
    hospital = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return f"Dr. {self.name} ({self.specialization})"
