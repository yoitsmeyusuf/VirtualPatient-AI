# 🏥 AntrenmanAI

**Tıp öğrencileri için AI destekli hasta simülasyonu ve klinik pratik platformu.**

GPT-4o-mini ile gerçekçi hasta senaryoları oluşturur, doğal Türkçe hasta sohbeti sağlar, performansı değerlendirir ve ELO tabanlı gamification ile öğrenmeyi oyunlaştırır. MVP

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Vite-6-646CFF?logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-3-06B6D4?logo=tailwindcss&logoColor=white" />
  <img src="https://img.shields.io/badge/AI-GPT--4o--mini-412991?logo=openai&logoColor=white" />
</p>

---

## ✨ Özellikler

### 🎭 AI Hasta Aktör
- GPT-4o-mini ile doğal Türkçe hasta sohbeti
- Dinamik **duygu modeli** — doktorun tutumuna göre hasta tepkisi değişir (sinirli, endişeli, rahatlamış...)
- Kişilik tipleri: konuşkan, ketum, endişeli, sinirli, yaşlı-ağır

### 📋 Klinik Senaryo Üretimi
- **3 zorluk seviyesi:** Kolay / Orta / Zor
- Tam profil: anamnez, vital bulgular, fizik muayene, lab sonuçları, görüntüleme
- Gerçekçi Türk hasta isimleri ve kültürel bağlam

### 🩺 Tam Klinik Döngü
- **Anamnez** → Hasta ile sohbet
- **Fizik muayene** → Bölge bazlı bulgular
- **Tetkik isteme** → Lab & görüntüleme sonuçları
- **Tanı koyma** → AI destekli tanı tahmini
- **Tedavi planlama** → Reçete yazma + AI değerlendirmesi

### 💡 Akıl Hocası (Tutor AI)
- Sokratik yöntemle ipuçları
- 3 seviye: hafif → orta → güçlü
- Doğru tanıyı söylemeden yönlendirme

### 📊 Kapsamlı Değerlendirme
- 6 kategori: anamnez, muayene, tetkik, klinik muhakeme, iletişim, profesyonellik
- Tedavi planı değerlendirmesi (ilaç seçimi, doz, güvenlik)
- Alerji çakışması ve ilaç etkileşimi kontrolü

### 🎮 Gamification
- **ELO Rating** — FIDE satranç sistemi benzeri (K=32)
- **XP & Seviye** sistemi (her 500 XP = 1 seviye)
- **16 rozet:** İlk Adım, Keskin Göz, Mükemmel Skor, Efsane Doktor...
- **Liderlik tablosu** — Başlangıç / Bronz / Gümüş / Altın / Efsane tierleri
- **Streak sistemi** — Günlük seri takibi

### 🔐 Kimlik Doğrulama
- Google OAuth 2.0 + JWT
- Dev mode: `GOOGLE_CLIENT_ID` ayarlanmadığında otomatik geliştirici girişi

---

## 🏗️ Mimari

```
AntrenmanAI/
├── ai-service/              # Python Backend
│   ├── main.py              # FastAPI — 18 route, lifespan DB init
│   ├── api_services.py      # OpenAI API çağrıları (7 fonksiyon)
│   ├── prompts.py           # 7 sistem prompt şablonu
│   ├── database.py          # SQLite + aiosqlite (ELO/XP/rozet)
│   ├── auth.py              # Google OAuth + JWT
│   ├── config.py            # Pydantic Settings
│   ├── requirements.txt
│   └── test_full.py         # 14 endpoint kapsamlı test
│
├── frontend/                # React Frontend
│   ├── src/
│   │   ├── App.jsx          # 5 ekran + navigasyon
│   │   ├── api.js           # 14 API fonksiyonu
│   │   └── components/
│   │       ├── StartScreen.jsx       # Konu + zorluk seçimi
│   │       ├── SimulationScreen.jsx  # Sohbet + duygu + ipucu
│   │       ├── ChatPanel.jsx         # Mesajlaşma arayüzü
│   │       ├── PatientInfo.jsx       # Hasta bilgi kartı
│   │       ├── ActionPanel.jsx       # Muayene & tetkik
│   │       ├── TreatmentPanel.jsx    # Tedavi planlama
│   │       ├── EvaluationReport.jsx  # Performans + gamification
│   │       ├── ProfileScreen.jsx     # Profil + istatistikler
│   │       └── LeaderboardScreen.jsx # ELO sıralaması
│   ├── package.json
│   └── vite.config.js
│
└── .gitignore
```

---

## 🚀 Kurulum

### Gereksinimler
- Python 3.11+
- Node.js 18+
- OpenAI API anahtarı (GPT-4o-mini erişimi)

### 1. Backend

```bash
cd ai-service

# Virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Bağımlılıklar
pip install -r requirements.txt

# Ortam değişkenleri
cp .env.example .env
# .env dosyasını düzenle: EXTERNAL_API_KEY=sk-...
```

### 2. Frontend

```bash
cd frontend
npm install
```

### 3. Ortam Değişkenleri (`.env`)

```env
EXTERNAL_API_KEY=sk-proj-...       # OpenAI API anahtarı
MODEL=gpt-4o-mini
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID_HERE  # Boş bırakırsan dev mode
JWT_SECRET=super-secret-key-change-me
APP_HOST=0.0.0.0
APP_PORT=8000
```

---

## ▶️ Çalıştırma

**Terminal 1 — Backend:**
```bash
cd ai-service
python main.py
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
# → http://localhost:3000
```

---

## 🧪 Test

```bash
cd ai-service

# Sunucu çalışırken, başka terminalde:
python test_full.py
```

14 endpoint'i sırayla test eder:
- 🔐 Auth (login + JWT doğrulama)
- 🎬 Senaryo üretimi (3 zorluk)
- 💬 Hasta sohbeti + duygu analizi (4 tur)
- 🩺 Fizik muayene (4 bölge)
- 🧪 Tetkik isteme (5 tetkik)
- 💡 Tutor ipucu
- 💊 Tedavi değerlendirmesi
- 🔬 Hastalık tahmini
- 📊 Performans değerlendirmesi + ELO/XP
- 👤 Profil, 🏆 Liderlik, 🏅 Rozetler, 📜 Oturum geçmişi
- 🛡️ Hata dayanıklılığı testleri

---

## 📡 API Endpoint'leri

| Metot | Yol | Açıklama |
|-------|-----|----------|
| `POST` | `/auth/google` | Google OAuth ile giriş |
| `GET` | `/auth/me` | JWT ile kullanıcı bilgisi |
| `GET` | `/` | Sağlık kontrolü |
| `POST` | `/generate_scenario` | Senaryo üretimi (zorluk seviyeli) |
| `POST` | `/chat` | Hasta sohbeti + duygu analizi |
| `POST` | `/examine` | Fizik muayene bulguları |
| `POST` | `/order_test` | Lab & görüntüleme sonuçları |
| `POST` | `/evaluate` | Performans değerlendirmesi + ELO/XP |
| `POST` | `/diagnose` | AI tanı tahmini |
| `POST` | `/hint` | Tutor AI ipucu |
| `POST` | `/treatment` | Tedavi planı değerlendirmesi |
| `GET` | `/profile` | Kullanıcı istatistikleri |
| `GET` | `/leaderboard` | ELO liderlik tablosu |
| `GET` | `/achievements` | Kazanılan rozetler |
| `GET` | `/sessions` | Oturum geçmişi |

> 📄 Detaylı API dökümantasyonu: `http://localhost:8000/docs`

---

## 🎯 ELO Rating Sistemi

FIDE satranç rating sisteminden esinlenilmiştir:

```
ELO Değişimi = K × (Gerçek Skor − Beklenen Skor)

K = 32
Beklenen Skor:
  Kolay → 0.75  (kazanman bekleniyor)
  Orta  → 0.50  (50/50)
  Zor   → 0.25  (kaybetmen bekleniyor)
```

| Tier | ELO Aralığı | Rozet |
|------|-------------|-------|
| Başlangıç | < 1200 | 🩺 |
| Bronz | 1200–1499 | 🥉 |
| Gümüş | 1500–1799 | 🥈 |
| Altın | 1800–1999 | 🥇 |
| Efsane | 2000+ | 💎 |

---

## 🛠️ Teknoloji Stack

| Katman | Teknoloji |
|--------|-----------|
| **AI** | OpenAI GPT-4o-mini |
| **Backend** | Python 3.13, FastAPI, Pydantic |
| **Database** | SQLite + aiosqlite |
| **Auth** | Google OAuth 2.0, PyJWT |
| **Frontend** | React 18, Vite 6, Tailwind CSS 3 |
| **UI Icons** | Lucide React |
