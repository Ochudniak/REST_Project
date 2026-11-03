from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

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

class UserCreateViewTest(APITestCase):
    def test_create_user(self):

        data = {
            "name": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
        }

        response = self.client.post("/api/users/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(email="test@example.com").count(), 1)

        user = User.objects.get(email="test@example.com")

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.name, "testuser")

        self.assertNotIn("password", response.data)

    def test_create_user_without_name(self):

        data = {"name": "", "email": "test@example.com", "password": "Password123"}

        response = self.client.post("/api/users/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_password(self):
        data = {"name": "Name", "email": "test@example.com", "password": ""}

        response = self.client.post("/api/users/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_email(self):

        data = {"name": "", "email": "", "password": "Password123"}

        response = self.client.post("/api/users/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_wrong_email(self):

        data = {"name": "testuser", "email": "not-an-email", "password": "Password123"}

        response = self.client.post("/api/users/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_duplicated_email(self):
        User.objects.create(
            name="firstuser",
            email="test@example.com",
            password="Password123",
        )

        data = {
            "name": "seconduser",
            "email": "test@example.com",
            "password": "AnotherPassword123",
        }

        response = self.client.post("/api/users/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.filter(email="test@example.com").count(), 1)


class UserViewDetailTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            name="testuser", email="test@example.com", password="testpassword"
        )

    def test_find_user(self):
        response = self.client.get(f"/api/users/{self.user.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["email"], "test@example.com")

    def test_find_user_wrong_id_format(self):
        response = self.client.get("/api/users/abc/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_find_user_that_dont_exist(self):
        response = self.client.get("/api/users/99999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user(self):
        data = {
            "name": "updatedname",
            "email": "updated@example.com",
            "password": "updatedpassword",
        }

        response = self.client.put(f"/api/users/{self.user.id}/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, "updatedname")
        self.assertEqual(self.user.email, "updated@example.com")
        self.assertEqual(self.user.password, "updatedpassword")

    def test_update_user_that_dont_exist(self):
        data = {
            "name": "updatedname",
            "email": "updated@example.com",
            "password": "updatedpassword",
        }

        response = self.client.put("/api/users/99999/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user_with_wrong_email(self):
        data = {
            "name": "updatedname",
            "email": "wrongemail",
            "password": "updatedpassword",
        }

        response = self.client.put(f"/api/users/{self.user.id}/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_with_no_email(self):
        data = {
            "name": "updatedname",
            "email": "",
            "password": "updatedpassword",
        }

        response = self.client.put(f"/api/users/{self.user.id}/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_with_no_password(self):
        data = {
            "name": "updatedname",
            "email": "updated@example.com",
            "password": "",
        }

        response = self.client.put(f"/api/users/{self.user.id}/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_with_no_name(self):
        data = {
            "name": "",
            "email": "updated@example.com",
            "password": "updatedpassword",
        }

        response = self.client.put(f"/api/users/{self.user.id}/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_user(self):
        response = self.client.delete(f"/api/users/{self.user.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_user_that_dont_exist(self):
        response = self.client.delete("/api/users/99999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
