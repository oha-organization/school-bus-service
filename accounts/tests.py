from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LoginPageTests(TestCase):
    def test_url_exists_at_correct_location_loginview(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)

    def test_login_view_name(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_login_form(self):
        testuser = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
        )
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password1": "testpass123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertEqual(get_user_model().objects.all()[0].username, "testuser")
        self.assertEqual(get_user_model().objects.all()[0].email, "testuser@email.com")
        self.assertEqual(get_user_model().objects.get(id=1).username, "testuser")
        self.assertEqual(get_user_model().objects.get(id=1), testuser)
