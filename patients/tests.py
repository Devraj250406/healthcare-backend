from rest_framework import status

from healthcare.test_utils import AuthenticatedAPITestCase

from .models import Patient


class PatientTests(AuthenticatedAPITestCase):
    url = "/api/patients/"
    payload = {"name": "John Doe", "date_of_birth": "1990-05-20", "gender": "male", "phone": "+91 98765 43210"}

    def setUp(self):
        self.user = self.make_user()
        self.other = self.make_user("bob@example.com", "Bob")
        self.authenticate(self.user)

    def test_requires_authentication(self):
        self.client.credentials()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crud_flow(self):
        res = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        pid = res.data["id"]
        self.assertEqual(res.data["created_by"], self.user.id)

        res = self.client.get(f"{self.url}{pid}/")
        self.assertEqual(res.data["name"], "John Doe")

        res = self.client.put(f"{self.url}{pid}/", {**self.payload, "name": "John Smith"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "John Smith")

        res = self.client.delete(f"{self.url}{pid}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(pk=pid).exists())

    def test_list_only_returns_own_patients(self):
        Patient.objects.create(created_by=self.other, name="Hidden", date_of_birth="1980-01-01", gender="female")
        self.client.post(self.url, self.payload, format="json")
        res = self.client.get(self.url)
        self.assertEqual([p["name"] for p in res.data], ["John Doe"])

    def test_cannot_access_other_users_patient(self):
        p = Patient.objects.create(created_by=self.other, name="Hidden", date_of_birth="1980-01-01", gender="female")
        for method in ("get", "put", "delete"):
            res = getattr(self.client, method)(f"{self.url}{p.id}/", self.payload, format="json")
            self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Patient.objects.filter(pk=p.id).exists())

    def test_validation_errors(self):
        res = self.client.post(
            self.url, {"name": " ", "date_of_birth": "2999-01-01", "gender": "x", "phone": "abc"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            set(res.data["error"]["details"]), {"name", "date_of_birth", "gender", "phone"}
        )
