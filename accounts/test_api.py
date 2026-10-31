import shutil
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import User

MEDIA_TESTE = tempfile.mkdtemp()


class AuthApiTest(APITestCase):
    def test_cadastro_devolve_token(self):
        data = {
            "username": "ana",
            "email": "ana@exemplo.com",
            "password": "Senha-forte-123",
            "name": "Ana",
        }
        response = self.client.post(reverse("register"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertNotIn("password", response.data)

    def test_cadastro_rejeita_senha_fraca(self):
        data = {"username": "ana", "email": "ana@exemplo.com", "password": "123"}
        response = self.client.post(reverse("register"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_login_devolve_token(self):
        User.objects.create_user(
            username="ana", email="ana@exemplo.com", password="Senha-forte-123"
        )
        data = {"username": "ana", "password": "Senha-forte-123"}
        response = self.client.post(reverse("login"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)


@override_settings(MEDIA_ROOT=MEDIA_TESTE)
class MeApiTest(APITestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_TESTE, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username="ana", email="ana@exemplo.com", password="Senha-forte-123"
        )
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

    def test_me_exige_login(self):
        self.client.credentials()
        response = self.client.get(reverse("me"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_altera_so_o_nome(self):
        response = self.client.patch(
            reverse("me"), {"name": "Ana Souza"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Ana Souza")
        self.assertEqual(self.user.bio, "")

    def test_envia_foto_de_perfil(self):
        imagem = BytesIO()
        Image.new("RGB", (10, 10), "teal").save(imagem, "PNG")
        foto = SimpleUploadedFile(
            "foto.png", imagem.getvalue(), content_type="image/png"
        )
        response = self.client.patch(
            reverse("me"), {"avatar": foto}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.avatar.name.startswith("avatars/"))

    def test_troca_senha_exige_senha_atual(self):
        data = {"current_password": "errada", "new_password": "Outra-senha-456"}
        response = self.client.post(reverse("change-password"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_troca_senha(self):
        data = {
            "current_password": "Senha-forte-123",
            "new_password": "Outra-senha-456",
        }
        response = self.client.post(reverse("change-password"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Outra-senha-456"))
