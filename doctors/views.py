from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from healthcare.permissions import IsCreatorOrReadOnly

from .models import Doctor
from .serializers import DoctorSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    """CRUD for doctors.

    Doctors form a shared directory: every authenticated user can list and view
    them, but only the user who added a doctor can update or delete it.
    """

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsCreatorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
