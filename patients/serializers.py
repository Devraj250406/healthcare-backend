from datetime import date

from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            "id", "name", "date_of_birth", "age", "gender", "email", "phone",
            "address", "medical_history", "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "age", "created_by", "created_at", "updated_at"]

    def get_age(self, obj):
        today = date.today()
        dob = obj.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name cannot be blank.")
        return value

    def validate_date_of_birth(self, value):
        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        if value.year < 1900:
            raise serializers.ValidationError("Date of birth is not realistic.")
        return value
