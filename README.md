# ⚡ Real-Time Chat (Django REST Framework + WebSocket + JWT)

Ushbu loyiha talabalar va o'rganuvchilar uchun **REST API** va **WebSocket** texnologiyalarining birgalikdagi integratsiyasini amaliy o'rgatish maqsadida yaratilgan.

---

## 🎯 Arxitektura va Ishlash Prinsipi (Flow)

Loyiha quyidagi asosiy zanjir bo'yicha ishlaydi:

```
[Browser / Swagger]
        │
        │ POST /api/messages/ (Bearer JWT)
        ▼
[Django REST Framework] (MessageCreateAPIView)
        │
        │ 1. Xabarni SQLite bazasiga saqlaydi
        │ 2. async_to_sync(channel_layer.group_send)() chaqiradi
        ▼
[Channels Group] (user-{id})
        │
        │ "type": "send_message"
        ▼
[ChatConsumer] (send_message metodi)
        │
        │ WebSocket orqali xabar yuboriladi
        ▼
[Browser] (socket.onmessage -> Xabarni real-time ekranda ko'rsatadi)
```

---

## 📚 22 Asosiy Tushuncha (O'quvchilar uchun qo'llanma)

### 1. Project nima?
Bu Django va Django Channels yordamida qurilgan gibrid (REST API + WebSocket) real-time xabarlashuv tizimi. Bu yerda xabarlar oddiy HTTP POST orqali yuboriladi, ammo qabul qilish real-time WebSocket orqali amalga oshiriladi.

### 2. HTTP nima?
HTTP (Hypertext Transfer Protocol) — bir tomonlama so'rov-javob (Request-Response) protokol hisoblanadi. Klient serverga so'rov yuboradi, server javob beradi va aloqa uziladi. Server o'z tashabbusi bilan klientga xabar yubora olmaydi.

### 3. WebSocket nima?
WebSocket — doimiy ochiq qoluvchi ikki tomonlama (Full-Duplex) aloqa kanali. Bir marta handshake (ulanuv) amalga oshirilgach, server istalgan paytda klientga real-time ma'lumot jo'nata oladi (sahifani yangilamasdan).

### 4. REST API nima?
REST API (Representational State Transfer) — HTTP protokoli orqali ma'lumotlar bilan ishlash (CRUD) uchun qoidalar to'plami. Bizning loyihamizda u ma'lumotlarni saqlash va tekshirish (`POST /api/messages/`) uchun javobgar.

### 5. JWT nima?
JWT (JSON Web Token) — xavfsiz, imzolangan ma'lumot uzatish standarti. U `header`, `payload`, `signature` qismlaridan iborat. Foydalanuvchi tizimga kirgach `access` va `refresh` token oladi va keyingi so'rovlarda `Authorization: Bearer <token>` orqali o'zini tanitadi.

### 6. Channels nima?
Django Channels — Djangoni an'anaviy HTTP doirasidan chiqarib, WebSocket, MQTT kabi asinxron protokollarni qo'llab-quvvatlash imkoniyatini beruvchi rasmiy kutubxona.

### 7. ASGI nima?
ASGI (Asynchronous Server Gateway Interface) — Python asinxron veb-serverlari (masalan, Daphne) va asinxron Django ilovasi o'rtasidagi zamonaviy standart ko'prik. An'anaviy WSGI faqat sinxron HTTP bilan cheklangan.

### 8. Consumer nima?
Consumer — Channels'dagi xuddi Django View'ning asinxron analogi. U WebSocket ulanishlarini qabul qiladi, voqealarni (events) tinglaydi va klient bilan jonli aloqani ushlab turadi.

### 9. Channel Layer nima?
Channel Layer — bir nechta consumerlar, jarayonlar yoki REST API va WebSocket o'rtasida xabarlar almashish imkonini beruvchi aloqa tizimi. Birinchi bosqichda biz operativ xotirada ishlovchi `InMemoryChannelLayer` ishlatamiz.

### 10. Group nima?
Group — bir nechta kanal ulanishlarini birlashtiruvchi virtual guruh. Loyihamizda har bir foydalanuvchi uchun unikal guruh (`user-1`, `user-2`) ochiladi.

### 11. group_add nima?
`channel_layer.group_add(group_name, channel_name)` — ma'lum bir WebSocket ulanishini (channel) guruhga a'zo qiladi.

### 12. group_send nima?
`channel_layer.group_send(group_name, event_dict)` — guruhga tegishli barcha kanallarga hodisa (event) yuboradi.

### 13. group_discard nima?
`channel_layer.group_discard(group_name, channel_name)` — ulanish uzilganda kanalni guruhdan chiqarib tashlaydi.

### 14. scope["user"] nima?
ASGI so'rovlarida `request.user` o'rniga `scope["user"]` ishlatiladi. Bizning JWT middleware'imiz tokenni tekshirib, foydalanuvchi obyektini aynan `scope["user"]` ga joylashtiradi.

### 15. REST API → WebSocket flow nima?
Bu REST API orqali biznes logikani (validatsiya, permission, DB saqlash) bajarib, so'ngra WebSocket orqali klientga tezkor xabar uzatish arxitekturasi.

### 16. ws:// nima?
`ws://` — shifrlanmagan WebSocket protokoli (HTTP analogi, port 80 yoki 8000).

### 17. wss:// nima?
`wss://` — TLS/SSL bilan shifrlangan xavfsiz WebSocket protokoli (HTTPS analogi, port 443).

### 18. Swagger qanday ishlatiladi?
Swagger (`drf-spectacular`) — API endpointlarni vizual interfeys orqali test qilish, parametrlarni kiritish va javoblarni ko'rish imkonini beruvchi qulay vosita.

### 19. Projectni qanday ishga tushirish?
Pastdagi "Bosqichma-bosqich qo'llanma" bo'limiga qarang.

### 20. Troubleshooting nima?
Xatoliklarni aniqlash va ularni tizimli ravishda bartaraf etish jarayoni.

---

## 🚀 Bosqichma-bosqich Ishga Tushirish (Quickstart)

### 1-QADAM: Virtual Muhitni Yaratish va Faollashtirish
```bash
python3 -m venv venv

# macOS / Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 2-QADAM: Kerakli Kutubxonalarni O'rnatish
```bash
pip install -r requirements.txt
```

### 3-QADAM: Migratsiyalarni Bajarish
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4-QADAM: Test Foydalanuvchisini Yaratish
```bash
# Superuser yaratish (ixtiyoriy):
python manage.py createsuperuser

# Yoki avtomatik student yaratish:
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='student').exists() or User.objects.create_user('student', 'student@example.com', 'password123')"
```

### 5-QADAM: Serverni Ishga Tushirish
```bash
python manage.py runserver
```
*(Server Daphne orqali HTTP va WebSocket'ni birgalikda 8000-portda boshqaradi)*

---

## 🧪 Swagger va Real-Time Sinov Qo'llanmasi (Test Flow)

1. **Swagger'ni oching**:
   Brauzerda `http://127.0.0.1:8000/api/docs/` manziliga kiring.
2. **Token olish**:
   `POST /api/token/` endpointini oching va **Try it out** tugmasini bosing.
   Body'ga kiriting:
   ```json
   {
       "username": "student",
       "password": "password123"
   }
   ```
   **Execute** bosing va qaytgan `access` tokenni nusxalab oling.
3. **Avtorizatsiya (Authorize)**:
   Swagger sahifasining yuqori o'ng burchagidagi **Authorize** tugmasini bosing.
   Oynaga nusxalangan tokenni joylang (format: `Bearer <access_token>` yoki to'g'ridan-to'g'ri token).
4. **Chat sahifasini oching**:
   Boshqa tabda `http://127.0.0.1:8000/` manzilini oching.
   `student` va `password123` bilan **Kirish** tugmasini bosing.
   Status indikatori **"Ulangan (Active)"** bo'lganiga ishonch hosil qiling.
5. **Swagger orqali xabar jo'nating**:
   Swagger'ga qaytib, `POST /api/messages/` endpointiga kiring:
   ```json
   {
       "message": "Salom! Bu Swagger'dan yuborilgan real-time xabar!"
   }
   ```
   **Execute** tugmasini bosing (HTTP 201 qaytadi).
6. **Natijani ko'ring**:
   Chat tabiga qarang: Xabar sahifa yangilanmasdan (real-time) ekranda paydo bo'ladi!

---

## 🛠 Troubleshooting (Eng ko'p uchraydigan 6 ta xatolik)

### 1. `Identifier 'socket' has already been declared`
- **Sababi**: Brauzer konsolida `const socket = ...` kodi qayta-qayta ishga tushirilgan. `const` o'zgaruvchini qayta e'lon qilib bo'lmaydi.
- **Yechim**: Mavjud `socket` obyektidan foydalaning (masalan, `socket.readyState`) yoki brauzer sahifasini to'liq yangilang (`Ctrl + F5` / `Cmd + Shift + R`).

### 2. `readyState = 3`
- **Sababi**: WebSocket ulanishining holati `CLOSED` (yopiq).
- **Yechim**: Server ishlab turganini va token to'g'ri ekanini tekshiring, so'ngra qayta login qiling.

### 3. `WebSocket is already in CLOSING or CLOSED state`
- **Sababi**: Ulanish yopilganidan keyin `socket.send()` chaqirilgan.
- **Yechim**: Xabarlarni `socket.send()` orqali emas, balki REST API (`POST /api/messages/`) orqali yuboring.

### 4. `404 /ws/chat/`
- **Sababi**: WebSocket routing noto'g'ri sozlangan yoki so'rov URL'i adashgan.
- **Yechim**: `config/asgi.py` da `URLRouter(websocket.routing.websocket_urlpatterns)` ulanganini va manzil `ws://127.0.0.1:8000/ws/chat/?token=...` ekanini tekshiring.

### 5. `AnonymousUser`
- **Sababi**: JWT token taqdim etilmagan, eskirgan yoki imzo mos kelmagan.
- **Yechim**: `POST /api/token/` orqali yangi access token oling va query parameterda to'g'ri uzating.

### 6. WebSocket connected, lekin xabar kelmayapti
- **Sababi**: REST API'dagi group nomi (`f"user-{request.user.id}"`) va Consumer'dagi group nomi bir-biriga mos emas.
- **Yechim**: Har ikkala joyda ham format `user-{user.id}` ekanligini ta'minlang.

---

## 🔜 Keyingi Qadam: Redis (Next Step)

Hozirgi bosqichda biz xotirada ishlovchi `InMemoryChannelLayer` ishlatdik.
Biroq, tizimni bir nechta server va jarayonlarda masshtablash uchun Redis talab etiladi:

1. Kutubxona o'rnatiladi:
   ```bash
   pip install channels-redis
   ```
2. `config/settings.py` dagi `CHANNEL_LAYERS` almashtiriladi:
   ```python
   CHANNEL_LAYERS = {
       "default": {
           "BACKEND": "channels_redis.core.RedisChannelLayer",
           "CONFIG": {
               "hosts": [("127.0.0.1", 6379)],
           },
       },
   }
   ```

---

## 🌐 Production Arxitekturasi

Production muhitida quyidagi zanjir tavsiya etiladi:

```
[Mijoz Brauzeri]
       │
       ▼ (HTTPS / WSS - Port 443)
    [Nginx] (SSL Terminirovka va Static fayllar)
       │
       ├── /api/ va / -> [Gunicorn / Daphne]
       │
       └── /ws/ -> [Daphne ASGI Server] (Proxy WebSocket)
                         │
                         ▼
                [Redis Channel Layer]
```
