from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    register_url = "/api/auth/register/"
    login_url = "/api/auth/login/"

    def register(self, **overrides):
        data = {"name": "Alice", "email": "Alice@Example.com", "password": "Str0ng-Passw0rd!"}
        data.update(overrides)
        return self.client.post(self.register_url, data, format="json")

    def test_register_creates_user_and_returns_tokens(self):
        res = self.register()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["user"]["email"], "alice@example.com")
        self.assertIn("access", res.data)
        self.assertNotIn("password", res.data["user"])
        self.assertTrue(User.objects.get(email="alice@example.com").check_password("Str0ng-Passw0rd!"))

    def test_register_rejects_duplicate_email(self):
        self.register()
        res = self.register(email="ALICE@example.com")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res.data["success"])
        self.assertIn("email", res.data["error"]["details"])

    def test_register_rejects_weak_password_and_missing_fields(self):
        res = self.register(password="123")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", res.data["error"]["details"])
        res = self.client.post(self.register_url, {}, format="json")
        self.assertEqual(set(res.data["error"]["details"]), {"name", "email", "password"})

    def test_login_returns_jwt(self):
        self.register()
        res = self.client.post(
            self.login_url, {"email": "ALICE@example.com", "password": "Str0ng-Passw0rd!"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertEqual(res.data["user"]["name"], "Alice")

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)

    def test_login_with_wrong_password_fails(self):
        self.register()
        res = self.client.post(
            self.login_url, {"email": "alice@example.com", "password": "wrong"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res.data["error"]["message"], "Invalid email or password.")
