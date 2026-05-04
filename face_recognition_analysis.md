# Loyiha tahlili: Yuzni aniqlash tizimi (Face Recognition System)

**Turniket** loyihasidagi yuzni aniqlash tizimi Python tilida yozilgan bo'lib, u asosan Machine Learning modellari va `face_recognition` (dlib ustida qurilgan) kutubxonasiga asoslangan. Tizim markaziy mantiqini `backend/app/services/face_recognition_service.py` fayli o'zida saqlaydi.

Quyida uning to'liq qanday ishlashi bosqichma-bosqich yoritilgan:

## 1. Asosiy arxitektura (Singleton Service)
Tizim `FaceRecognitionService` klassida yozilgan bo'lib, barcha so'rovlar bitta instans (obyekt) yordamida qayta ishlanadi:
Bu yondashuv barcha kiruvchi so'rovlarga tez va yuz vektorlarini xotirada ushlab turish imkonini beradi. Qator jarayonlarda xatolik bo'lmasligi (Thread-safe) uchun ma'lumotlarni o'zgartirish paytida `Lock` mexanizmidan foydalanilgan.

## 2. Ma'lumotlarni keshda saqlash (Cache Management)
Yuzni tekshirish har bir soniyada bir necha bor ishlashi mumkin. Tizim past tezlikdagi baza (Database) ga har safar murojaat qilavermasligi uchun barcha yuz xarakteristikalarini RAM (xotira) da kesh qilib saqlaydi:
* `reload_encodings(db)`: Bu funksiya orqali bazadan barcha faol (`is_active == True`) foydalanuvchilar va ularning bazada saqlangan 128 o'lchamli yuz vektori numpy massiviga aylantirilib, xotiraga yuklanadi.
* Kesh `self._known` lug'atida saqlanadi. Uning formati: `user_id -> (name, encoding_vector)`.

## 3. Yuzni qidirish va vektor ajratish (Encoding extraction)
Kameralar tasvir yuborganida dasting kiruvchi tasvirda aynan nima borligini ko'radi. Buni rasmdan ma'lumot ajratish (`extract_encoding`) bajaradi:
1. **O'lchamni kichraytirish:** Tasvir juda katta bo'lsa hisoblash ham cho'ziladi. Shuning uchun avval tasvir kengligi 640px gacha kichraytiriladi.
2. **Rang formatini o'zgartirish:** Tizim `OpenCV` dan foydlangani sabab uning rangi `BGR` ko'rinishida keladi. Facerecognition kutubxonasi ishlashi uchun u oddiy `RGB` formatga o'tkaziladi.
3. **Yuzning joylashuvini topish:** `face_recognition.face_locations(rgb, model="hog")` orqali tasvirda xuddi inson yuziga o'xshash obyekt bormi yoki yo'qligi aniqlanadi. (Bunda asosan insonning ko'zlari, burni va yuz konturlari yordam beradi).
4. **128-o'lchamli vektor:** Yuz joylashuvi topilgandan so'ng uning o'ziga xos noyob (biometrik) chiziqlaridan iborat bo'lgan 128ta nuqtalar koordinatasi `face_encodings` yordamida yig'ib olinadi.

## 4. Taqqoslash va ruxsat berish (Recognition Pipeline)
Bu tahlilning va eng asosiy jarayonning yakuniy qismi bo'lib, xotiradagi (bazadagi) odamlar va kameradan kelayotgan odam orasidan bir xilini qidiradi. (Buni `recognize` funksiyasi bajaradi):
1. **Vektorni tayyorlash**: Kameradan kelgan harakatdagi kadrdan yuqorida aytib o'tilgan 128-o'lchamli vektor olinadi. Rasmda odam topilmasa, dasting ruxsatni to'xtatib `"No face detected"` statusi qaytaradi.
2. **Taqqoslash:** Olingan yangi vektor xotirada saqlanib turgan barcha minglab foydalanuvchilarning vektorlari bilan birdaniga solishtiriladi (`face_recognition.face_distance`). Bu algoritm kutubxonadagi Evklid masofasi formulasidan kelib chiqadi. Har ikki obyektning yuzlari orasidagi aniq masofani hisoblab beradi. Masofa qanchalik ro'l o'ynasa (qiymat qancha kichik bo'lsa), yuz shunchalik o'xshashligini bildiradi.
3. **Maksimal o'xshashlikni qidirish:** Hisoblanganlar ichidan eng qisqa masofaga ega bo'lgan shaxs (`np.argmin(distances)`) ya'ni masofadagi "Best ID" ajratib olinadi.
4. **Rozilik berish ssenariysi:** Ajratib olingan ehtimoliy Top-1 natija tizimning sozlangan chegaraviy talabi (masalan `FACE_DISTANCE_THRESHOLD` asosan 0.4 yoki 0.6 bo'ladi) bilan taqqoslanadi.
   * Agar best masofali natija ruxsat berilgan chegaradan **kichik yo teng** bo'lsa, tizim rozi bo'lib insonni tanigan hisoblanadi (`status: allowed`).
   * Aks holda, o'xshashlik yetarli emas deb o'ylaydi va eshikni ro'xast bermaydi (`status: denied`).

Ishtirokchilar bilishi uchun ishonch kofitsienti ham ko'rsatib boriladi. Foiz quyidagicha namoyon bo'ladi: `1.0 - best_distance`. Ya'ni agar distance 0.35 bo'lsa o'xshashlik koefitsienti `0.65` yo'ki 65%.

## Xulosa
Ushbu Python backend dagi loyiha arxitekturasi jarayonni sezilarli va tezroq qayta ishlashi uchun juda pishiq qilib ishlangan. Avval barcha userlarni xotirada saqlab, kelgan so'rovni CPU ni o'zida HOG modeli yordamida kichraytirilgan rasmda ishlatish tezkor, hamda aniq va stabil ishlash uchun yaxshi instrument qilingan. Buloq kodli, ma'lumotlarni parallel tahlil qilinmoqdalik jarayonlarida xatoliklarning oldi olingani a'lo yechimdir.
