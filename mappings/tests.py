from rest_framework import status

from doctors.models import Doctor
from healthcare.test_utils import AuthenticatedAPITestCase
from patients.models import Patient

from .models import PatientDoctorMapping


class MappingTests(AuthenticatedAPITestCase):
    url = "/api/mappings/"

    def setUp(self):
        self.user = self.make_user()
        self.other = self.make_user("bob@example.com", "Bob")
        self.patient = Patient.objects.create(created_by=self.user, name="John", date_of_birth="1990-01-01", gender="male")
        self.other_patient = Patient.objects.create(created_by=self.other, name="Jane", date_of_birth="1991-01-01", gender="female")
        self.doc1 = Doctor.objects.create(created_by=self.user, name="Meera", specialization="Cardiology", email="m@h.com")
        self.doc2 = Doctor.objects.create(created_by=self.other, name="Ravi", specialization="Neurology", email="r@h.com")
        self.authenticate(self.user)

    def assign(self, patient, doctor):
        return self.client.post(self.url, {"patient": patient.id, "doctor": doctor.id}, format="json")

    def test_assign_list_and_get_doctors_for_patient(self):
        self.assertEqual(self.assign(self.patient, self.doc1).status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.assign(self.patient, self.doc2).status_code, status.HTTP_201_CREATED)

        res = self.client.get(self.url)
        self.assertEqual(len(res.data), 2)

        res = self.client.get(f"{self.url}{self.patient.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 2)
        self.assertEqual({d["doctor"]["name"] for d in res.data["doctors"]}, {"Meera", "Ravi"})

    def test_cannot_assign_same_doctor_twice(self):
        self.assign(self.patient, self.doc1)
        res = self.assign(self.patient, self.doc1)
        self.assertEqual(res.status_code, 400)
        self.assertIn("doctor", res.data["error"]["details"])

    def test_cannot_assign_to_other_users_patient_or_missing_doctor(self):
        res = self.assign(self.other_patient, self.doc1)
        self.assertEqual(res.status_code, 400)
        self.assertIn("patient", res.data["error"]["details"])
        res = self.client.post(self.url, {"patient": self.patient.id, "doctor": 9999}, format="json")
        self.assertIn("doctor", res.data["error"]["details"])

    def test_cannot_view_other_users_patient_mappings(self):
        PatientDoctorMapping.objects.create(patient=self.other_patient, doctor=self.doc2, assigned_by=self.other)
        self.assertEqual(self.client.get(self.url).data, [])
        self.assertEqual(self.client.get(f"{self.url}{self.other_patient.id}/").status_code, 404)

    def test_delete_mapping(self):
        mapping_id = self.assign(self.patient, self.doc1).data["id"]
        self.assertEqual(self.client.delete(f"{self.url}{mapping_id}/").status_code, 204)
        self.assertFalse(PatientDoctorMapping.objects.exists())
        self.assertEqual(self.client.delete(f"{self.url}{mapping_id}/").status_code, 404)

    def test_cannot_delete_other_users_mapping(self):
        m = PatientDoctorMapping.objects.create(patient=self.other_patient, doctor=self.doc2, assigned_by=self.other)
        self.assertEqual(self.client.delete(f"{self.url}{m.id}/").status_code, 404)
        self.assertTrue(PatientDoctorMapping.objects.filter(pk=m.id).exists())
