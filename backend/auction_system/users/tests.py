from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import User as LegacyUser
from rest_framework.authtoken.models import Token

User = get_user_model()

class RegistrationTests(APITestCase):

    def test_register_user(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "MocneHaslo123!"
        }

        response = self.client.post(
            "/api/register/",
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        user = User.objects.get(username="testuser")

        self.assertNotEqual(
            user.password,
            "MocneHaslo123!"
        )

        self.assertTrue(
            user.check_password("MocneHaslo123!")
        )

class LoginTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testlogin",
            password="MocneHaslo123!"
        )

    def test_login_correct_password(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "testlogin",
                "password": "MocneHaslo123!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_login_wrong_password(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "testlogin",
                "password": "ZleHaslo123!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

class LegacyEndpointsTests(APITestCase):

    def test_old_registration_disabled(self):
        response = self.client.post(
            "/api/users/",
            {
                "name": "test",
                "email": "test@example.com",
                "password": "Password123!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_old_login_disabled(self):
        response = self.client.post(
            "/api/users/login/",
            {
                "email": "test@example.com",
                "password": "Password123!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_old_user_detail_disabled(self):
        response = self.client.get("/api/users/1/")

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

class AuthenticationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testauth",
            password="MocneHaslo123!"
        )
        self.token = Token.objects.create(user=self.user)

    def test_access_without_token(self):
        response = self.client.get("/api/auth/me/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_access_with_valid_token(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

        response = self.client.get("/api/auth/me/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["username"],
            "testauth"
        )

    def test_access_with_invalid_token(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token nieprawidlowytoken"
        )

        response = self.client.get("/api/auth/me/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )