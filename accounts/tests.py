from django.db import IntegrityError
from django.test import TestCase

from accounts.models import User


class UserModelTest(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user(
            username="ana", email="ana@exemplo.com", password="Senha-forte-123"
        )
        self.bruno = User.objects.create_user(
            username="bruno", email="bruno@exemplo.com", password="Senha-forte-123"
        )

    def test_seguir_nao_e_mutuo(self):
        self.ana.following.add(self.bruno)

        self.assertIn(self.bruno, self.ana.following.all())
        self.assertIn(self.ana, self.bruno.followers.all())
        self.assertNotIn(self.ana, self.bruno.following.all())

    def test_perfil_e_opcional(self):
        self.assertEqual(self.ana.name, "")
        self.assertEqual(self.ana.bio, "")
        self.assertFalse(self.ana.avatar)

    def test_email_unico(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="ana2", email="ana@exemplo.com", password="Senha-forte-123"
            )

    def test_mostra_o_arroba(self):
        self.assertEqual(str(self.ana), "@ana")
