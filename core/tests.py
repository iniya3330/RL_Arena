import re

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


def csrf_token_from(response):
    match = re.search(
        rb'name="csrfmiddlewaretoken" value="([^"]+)"',
        response.content,
    )
    if not match:
        raise AssertionError("Response did not render a CSRF token")
    return match.group(1).decode()


class CsrfFlowTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def test_login_and_signup_forms_accept_their_rendered_tokens(self):
        login_page = self.client.get(reverse("login"))
        self.assertIn("no-store", login_page["Cache-Control"])
        login_response = self.client.post(reverse("login"), {
            "email": "missing@example.test",
            "password": "not-a-password",
            "csrfmiddlewaretoken": csrf_token_from(login_page),
        })
        self.assertEqual(login_response.status_code, 200)

        signup_page = self.client.get(reverse("signup"))
        self.assertIn("no-store", signup_page["Cache-Control"])
        signup_response = self.client.post(reverse("signup"), {
            "name": "Test User",
            "email": "test@example.test",
            "password": "Password123!",
            "confirm": "different-password",
            "csrfmiddlewaretoken": csrf_token_from(signup_page),
        })
        self.assertEqual(signup_response.status_code, 200)

    def test_dashboard_and_admin_post_pages_render_csrf_tokens(self):
        player = User.objects.create_user(
            username="player@example.test",
            email="player@example.test",
            password="test-password",
        )
        self.client.force_login(player)
        dashboard = self.client.get(reverse("dashboard"))
        self.assertEqual(dashboard.status_code, 200)
        csrf_token_from(dashboard)

        admin = User.objects.create_user(
            username="admin@example.test",
            email="admin@example.test",
            password="test-password",
            is_staff=True,
        )
        self.client.force_login(admin)
        admin_panel = self.client.get(reverse("admin_panel"))
        self.assertEqual(admin_panel.status_code, 200)
        csrf_token_from(admin_panel)
