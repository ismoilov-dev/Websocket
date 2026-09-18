import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from channels.testing import WebsocketCommunicator
from config.asgi import application
from websocket.models import Message

User = get_user_model()


class RealTimeChatIntegrationTestCase(TestCase):
    """
    REST API, SimpleJWT, Database, va WebSocket integratsiyasini
    to'liq tekshiruvchi avtomatlashtirilgan testlar to'plami.
    """

    def setUp(self):
        # Test uchun foydalanuvchi yaratamiz
        self.user = User.objects.create_user(
            username="student",
            password="password123"
        )
        self.client = APIClient()

    def test_01_jwt_token_obtain_and_refresh(self):
        """
        POST /api/token/ va POST /api/token/refresh/ to'g'ri ishlashini tekshirish
        """
        response = self.client.post('/api/token/', {
            "username": "student",
            "password": "password123"
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        refresh_token = response.data["refresh"]

        # Refresh token orqali yangi access token olish
        refresh_response = self.client.post('/api/token/refresh/', {
            "refresh": refresh_token
        }, format='json')
        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn("access", refresh_response.data)

    def test_02_swagger_and_schema_endpoints(self):
        """
        /api/schema/ va /api/docs/ (Swagger UI) 200 OK qaytarishini tekshirish
        """
        schema_res = self.client.get('/api/schema/')
        self.assertEqual(schema_res.status_code, 200)

        docs_res = self.client.get('/api/docs/')
        self.assertEqual(docs_res.status_code, 200)

    def test_03_message_post_unauthenticated(self):
        """
        Tokensiz POST /api/messages/ yuborilganda 401 Unauthorized qaytishi kerak
        """
        response = self.client.post('/api/messages/', {
            "message": "Salom testsiz"
        }, format='json')
        self.assertEqual(response.status_code, 401)

    def test_04_message_post_authenticated_and_db_save(self):
        """
        JWT token bilan POST /api/messages/ muvaffaqiyatli saqlanib, 201 Created qaytishi
        """
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post('/api/messages/', {
            "message": "Salom WebSocket REST orqali!"
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message"], "Salom WebSocket REST orqali!")
        self.assertEqual(response.data["user"], "student")

        # Bazada saqlanganini tekshirish
        self.assertTrue(Message.objects.filter(message="Salom WebSocket REST orqali!").exists())

    async def test_05_websocket_connection_unauthenticated(self):
        """
        Tokensiz yoki noto'g'ri token bilan ulanish 4001 close code bilan yopilishi kerak
        """
        communicator = WebsocketCommunicator(application, "/ws/chat/")
        connected, close_code = await communicator.connect()
        # Authenticated bo'lmagani uchun yopiladi (close_code=4001)
        self.assertFalse(connected)
        self.assertEqual(close_code, 4001)
        await communicator.disconnect()

    async def test_06_websocket_full_flow_rest_to_ws(self):
        """
        REST API -> Database -> group_send() -> ChatConsumer -> WebSocket to'liq oqimi
        """
        # 1. User uchun JWT access token yaratamiz
        access_token = str(AccessToken.for_user(self.user))

        # 2. WebSocket ulanishini ochamiz
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/?token={access_token}"
        )
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected, "WebSocket muvaffaqiyatli ulanishi shart!")

        # 3. Dastlabki welcome xabari kelganini tekshiramiz
        welcome_response = await communicator.receive_json_from()
        self.assertEqual(welcome_response["type"], "connection_established")
        self.assertEqual(welcome_response["user"], "student")
        self.assertEqual(welcome_response["group"], f"user-{self.user.id}")

        # 4. Endi REST API orqali xabar yuboramiz (baza + group_send)
        from asgiref.sync import sync_to_async
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        api_res = await sync_to_async(client.post)('/api/messages/', {
            "message": "Real-time integratsiya testi muvaffaqiyatli!"
        }, format='json')
        self.assertEqual(api_res.status_code, 201)

        # 5. WebSocket orqali bu xabar real-time kelganini tekshiramiz!
        ws_msg = await communicator.receive_json_from()
        self.assertEqual(ws_msg["type"], "chat_message")
        self.assertEqual(ws_msg["data"]["message"], "Real-time integratsiya testi muvaffaqiyatli!")
        self.assertEqual(ws_msg["data"]["user"], "student")

        # 6. Ulanishni yopamiz
        await communicator.disconnect()
