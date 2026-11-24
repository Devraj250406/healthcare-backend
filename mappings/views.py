from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from patients.models import Patient

from .models import PatientDoctorMapping
from .serializers import AssignedDoctorSerializer, PatientDoctorMappingSerializer


def mappings_for(user):
    return PatientDoctorMapping.objects.filter(patient__created_by=user).select_related(
        "patient", "doctor"
    )


class MappingListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/mappings/  - all patient-doctor mappings for the user's patients.
    POST /api/mappings/  - assign a doctor to one of the user's patients.
    """

    serializer_class = PatientDoctorMappingSerializer

    def get_queryset(self):
        return mappings_for(self.request.user)

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


class MappingDetailView(APIView):
    """
    The assignment specifies two routes with the same shape:

    GET    /api/mappings/<patient_id>/  - doctors assigned to a patient.
    DELETE /api/mappings/<id>/          - remove a mapping (by mapping id).

    So the path parameter means a patient id for GET and a mapping id for DELETE.
    """

    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        mappings = mappings_for(request.user).filter(patient=patient)
        return Response(
            {
                "patient_id": patient.id,
                "patient_name": patient.name,
                "count": mappings.count(),
                "doctors": AssignedDoctorSerializer(mappings, many=True).data,
            }
        )

    def delete(self, request, pk):
        mapping = get_object_or_404(mappings_for(request.user), pk=pk)
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
