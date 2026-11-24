from rest_framework import serializers

from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from patients.models import Patient

from .models import PatientDoctorMapping


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.none())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)
    doctor_specialization = serializers.CharField(source="doctor.specialization", read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = [
            "id", "patient", "patient_name", "doctor", "doctor_name",
            "doctor_specialization", "notes", "assigned_at",
        ]
        read_only_fields = ["id", "assigned_at"]
        # Uniqueness is checked in validate() with a clearer message.
        validators = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None and request.user.is_authenticated:
            # Users can only assign doctors to their own patients.
            self.fields["patient"].queryset = Patient.objects.filter(created_by=request.user)

    def validate(self, attrs):
        if PatientDoctorMapping.objects.filter(
            patient=attrs["patient"], doctor=attrs["doctor"]
        ).exists():
            raise serializers.ValidationError(
                {"doctor": ["This doctor is already assigned to this patient."]}
            )
        return attrs


class AssignedDoctorSerializer(serializers.ModelSerializer):
    """A doctor assigned to a patient, together with the mapping it came from."""

    mapping_id = serializers.IntegerField(source="id", read_only=True)
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ["mapping_id", "doctor", "notes", "assigned_at"]
