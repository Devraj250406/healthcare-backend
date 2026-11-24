from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthenticatedAPITestCase(APITestCase):
    password = "Str0ng-Passw0rd!"

    def make_user(self, email="alice@example.com", name="Alice"):
        return User.objects.create_user(email=email, name=name, password=self.password)

    def authenticate(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
