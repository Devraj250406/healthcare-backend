from rest_framework import status

from healthcare.test_utils import AuthenticatedAPITestCase

from .models import Doctor


class DoctorTests(AuthenticatedAPITestCase):
    url = "/api/doctors/"
    payload = {"name": "Meera Rao", "specialization": "Cardiology", "email": "meera@hospital.com", "years_of_experience": 12}

    def setUp(self):
        self.user = self.make_user()
        self.other = self.make_user("bob@example.com", "Bob")
        self.authenticate(self.user)

    def test_requires_authentication(self):
        self.client.credentials()
        self.assertEqual(self.client.post(self.url, self.payload, format="json").status_code, 401)

    def test_crud_flow(self):
        res = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        did = res.data["id"]
        self.assertEqual(self.client.get(f"{self.url}{did}/").data["specialization"], "Cardiology")
        res = self.client.put(f"{self.url}{did}/", {**self.payload, "years_of_experience": 13}, format="json")
        self.assertEqual(res.data["years_of_experience"], 13)
        self.assertEqual(self.client.delete(f"{self.url}{did}/").status_code, 204)

    def test_all_doctors_listed_but_only_creator_can_modify(self):
        doc = Doctor.objects.create(created_by=self.other, name="Ravi", specialization="Neurology", email="ravi@h.com")
        res = self.client.get(self.url)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(self.client.get(f"{self.url}{doc.id}/").status_code, 200)
        res = self.client.put(f"{self.url}{doc.id}/", self.payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(f"{self.url}{doc.id}/").status_code, 403)

    def test_duplicate_email_and_bad_experience(self):
        self.client.post(self.url, self.payload, format="json")
        res = self.client.post(self.url, {**self.payload, "email": "MEERA@hospital.com", "years_of_experience": 100}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(set(res.data["error"]["details"]), {"email", "years_of_experience"})
