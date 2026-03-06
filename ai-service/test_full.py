"""
test_full.py — AntrenmanAI KAPSAMLI TEST BETİĞİ (v2.0)
═══════════════════════════════════════════════════════════════
Tüm 18 endpoint'i sırayla test eder:

  🔐 AUTH
    1. POST /auth/google        → Dev mode giriş + JWT al
    2. GET  /auth/me             → JWT ile kullanıcı bilgisi

  🏥 KLİNİK SİMÜLASYON
    3. POST /generate_scenario   → Zorluk seviyeli senaryo üretimi
    4. POST /chat                → Hasta sohbeti + duygu analizi (4 tur)
    5. POST /examine             → Fizik muayene (4 bölge)
    6. POST /order_test          → Tetkik isteme (4 tetkik)

  🧠 YENİ AI ÖZELLİKLERİ
    7. POST /hint                → Tutor AI ipucu
    8. POST /treatment           → Tedavi planı değerlendirmesi
    9. POST /diagnose            → Hastalık tahmini

  📊 DEĞERLENDİRME + GAMİFİCATİON
   10. POST /evaluate            → Performans + ELO/XP/Rozet
   11. GET  /profile             → Kullanıcı profili + istatistikler
   12. GET  /leaderboard         → ELO liderlik tablosu
   13. GET  /achievements        → Kazanılan rozetler
   14. GET  /sessions            → Oturum geçmişi

Kullanım:
  1. Sunucuyu başlat:  python main.py
  2. Başka terminal:   python test_full.py

Not: Dev mode'da çalışır (GOOGLE_CLIENT_ID ayarlanmamış).
"""

import json
import time
import requests
import sys

BASE_URL = "http://localhost:8000"

# ── Terminal renkleri ──────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BLUE   = "\033[94m"
MAGENTA= "\033[95m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

# ── Test sayaçları ─────────────────────────────────────────────────
PASS_COUNT = 0
FAIL_COUNT = 0
SKIP_COUNT = 0


def sep(title: str, icon: str = "🔹") -> None:
    print(f"\n{'━' * 64}")
    print(f"  {icon} {BOLD}{CYAN}{title}{RESET}")
    print(f"{'━' * 64}")


def sub_sep(title: str) -> None:
    print(f"\n  {DIM}{'─' * 50}{RESET}")
    print(f"  {BLUE}{title}{RESET}")


def pretty(data, max_lines: int = 30) -> str:
    text = json.dumps(data, indent=2, ensure_ascii=False)
    lines = text.split("\n")
    if len(lines) > max_lines:
        return "\n".join(lines[:max_lines]) + f"\n  ... ({len(lines) - max_lines} satır daha)"
    return text


def check(condition: bool, success_msg: str, fail_msg: str) -> bool:
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"    {GREEN}✅ {success_msg}{RESET}")
        return True
    else:
        FAIL_COUNT += 1
        print(f"    {RED}❌ {fail_msg}{RESET}")
        return False


def skip(msg: str):
    global SKIP_COUNT
    SKIP_COUNT += 1
    print(f"    {YELLOW}⏭️  ATLANILDI: {msg}{RESET}")


def api_get(path: str, token: str = "", timeout: int = 30):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.get(f"{BASE_URL}{path}", headers=headers, timeout=timeout)


def api_post(path: str, payload: dict, token: str = "", timeout: int = 120):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.post(
        f"{BASE_URL}{path}", json=payload, headers=headers, timeout=timeout
    )


# ═══════════════════════════════════════════════════════════════════
# YEDEK SENARYO (API başarısız olursa kullanılır)
# ═══════════════════════════════════════════════════════════════════
FALLBACK_SCENARIO = {
    "patient_name": "Ahmet Yılmaz",
    "age": 45,
    "gender": "Erkek",
    "occupation": "Muhasebeci",
    "personality": "Endişeli ve meraklı",
    "chief_complaint": "Birkaç gündür karnım ağrıyor, özellikle yemekten sonra artıyor",
    "history_of_present_illness": (
        "3 gündür karnının üst kısmında yanıcı tarzda ağrı var. "
        "Yemeklerden 30 dakika sonra şiddetleniyor. "
        "Mide ilacı alınca biraz rahatlamış."
    ),
    "past_medical_history": ["Hipertansiyon (5 yıl)"],
    "medications": ["Amlodipin 5mg"],
    "allergies": ["Penisilin"],
    "vital_signs": {
        "blood_pressure": "135/85 mmHg",
        "heart_rate": "78 bpm",
        "temperature": "36.8 °C",
        "respiratory_rate": "16/dk",
        "spo2": "%98",
    },
    "physical_exam_findings": {
        "general": "Hasta bilinci açık, koopere, hafif endişeli görünümde.",
        "abdomen": "Epigastrik bölgede palpasyonla hassasiyet mevcut. Defans ve rebound yok.",
        "chest": "Akciğer sesleri bilateral doğal, kalp S1-S2 ritmik.",
        "other": "Özellik yok.",
    },
    "lab_results": {
        "complete_blood_count": {
            "wbc": "7.200 /mm³ (normal)",
            "hemoglobin": "14.1 g/dL (normal)",
            "platelets": "245.000 /mm³ (normal)",
        },
        "biochemistry": {
            "glucose": "95 mg/dL (normal)",
            "creatinine": "0.9 mg/dL (normal)",
            "alt": "22 U/L (normal)",
            "ast": "19 U/L (normal)",
        },
        "urinalysis": "Makroskopik ve mikroskopik olarak normal.",
    },
    "imaging_results": {
        "xray": "Akciğer grafisi normal.",
        "ultrasound": "Karaciğer, safra kesesi, pankreas normal.",
        "ct_scan": None,
    },
    "correct_diagnosis": "Gastrit",
    "correct_treatment": {
        "medications": ["Pantoprazol 40mg 1x1", "Sukralfat süspansiyon 4x1"],
        "lifestyle": ["Baharatlı yiyeceklerden kaçınma", "Küçük ve sık öğünler"],
    },
    "difficulty_level": "Orta",
}


# ═══════════════════════════════════════════════════════════════════
#  0) SAĞLIK KONTROLÜ
# ═══════════════════════════════════════════════════════════════════
def test_health() -> bool:
    sep("0 — SAĞLIK KONTROLÜ  (GET /)", "💚")
    try:
        r = api_get("/")
        data = r.json()
        check(r.status_code == 200, f"Durum: {data.get('status')}", "Sunucu yanıt vermedi")
        check("AntrenmanAI" in data.get("service", ""), f"Servis: {data['service']}", "Yanlış servis")
        print(f"    📋 Model: {data.get('model', '?')}")
        return True
    except requests.ConnectionError:
        print(f"\n  {RED}{'═' * 50}")
        print(f"  ❌  SUNUCUYA BAĞLANILAMADI!")
        print(f"  → Önce sunucuyu başlat:  python main.py")
        print(f"  {'═' * 50}{RESET}")
        return False


# ═══════════════════════════════════════════════════════════════════
#  1) AUTH — Google Login (Dev Mode)
# ═══════════════════════════════════════════════════════════════════
def test_auth_login() -> str | None:
    sep("1 — AUTH: Google Login  (POST /auth/google)", "🔐")
    print(f"    {DIM}Dev mode — sahte Google token gönderiliyor{RESET}")

    payload = {"credential": "fake-dev-token-for-testing"}
    try:
        r = api_post("/auth/google", payload)
        data = r.json()
        check(r.status_code == 200, "Giriş başarılı", f"HTTP {r.status_code}: {r.text}")
        token = data.get("token", "")
        user = data.get("user", {})
        check(len(token) > 20, f"JWT alındı ({len(token)} karakter)", "JWT boş!")
        check(user.get("email") == "dev@antrenman.ai", f"Kullanıcı: {user.get('name')} ({user.get('email')})", "Kullanıcı bilgisi yanlış")
        return token
    except Exception as exc:
        print(f"    {RED}❌ HATA: {exc}{RESET}")
        return None


# ═══════════════════════════════════════════════════════════════════
#  2) AUTH — Me (JWT ile)
# ═══════════════════════════════════════════════════════════════════
def test_auth_me(token: str) -> None:
    sep("2 — AUTH: Kullanıcı Bilgisi  (GET /auth/me)", "👤")

    # JWT ile
    r = api_get("/auth/me", token=token)
    data = r.json()
    check(r.status_code == 200, "JWT doğrulandı", f"HTTP {r.status_code}")
    check("user" in data, f"Kullanıcı: {data.get('user', {}).get('name', '?')}", "user anahtarı yok")

    # JWT olmadan (401 bekleniyor)
    sub_sep("Token olmadan erişim denemesi")
    r2 = api_get("/auth/me")
    check(r2.status_code == 401, "401 Unauthorized — doğru davranış", f"Beklenen 401, aldık {r2.status_code}")


# ═══════════════════════════════════════════════════════════════════
#  3) SENARYO ÜRETİMİ (Zorluk seviyeli)
# ═══════════════════════════════════════════════════════════════════
def test_generate_scenario(token: str) -> tuple[dict | None, int | None]:
    sep("3 — SENARYO ÜRETİMİ  (POST /generate_scenario)", "🎬")

    difficulties = ["Kolay", "Orta", "Zor"]
    scenario = None
    session_id = None

    for diff in difficulties:
        sub_sep(f"Zorluk: {diff}")
        payload = {"topic": "karın ağrısı", "difficulty": diff}
        print(f"    {YELLOW}→ İstek: konu='karın ağrısı', zorluk='{diff}'{RESET}")

        try:
            t0 = time.time()
            r = api_post("/generate_scenario", payload, token=token, timeout=90)
            elapsed = time.time() - t0
            data = r.json()

            if r.status_code == 200:
                sc = data.get("scenario", {})
                sid = data.get("session_id")
                check(True, f"Senaryo üretildi — {elapsed:.1f}s", "")
                check("patient_name" in sc, f"Hasta: {sc.get('patient_name', '?')}, {sc.get('age', '?')} yaş", "patient_name eksik")
                check("correct_diagnosis" in sc, f"Tanı: {sc.get('correct_diagnosis', '?')}", "correct_diagnosis eksik")
                check(sid is not None, f"Session ID: {sid}", "Session ID yok (DB sorunu?)")

                # Son senaryoyu kullan (Orta zorluk tercih)
                if diff == "Orta" or scenario is None:
                    scenario = sc
                    session_id = sid
            else:
                check(False, "", f"HTTP {r.status_code}: {data}")

        except requests.Timeout:
            check(False, "", f"Zaman aşımı ({diff})")
        except Exception as exc:
            check(False, "", f"Hata: {exc}")

    if scenario is None:
        print(f"\n    {YELLOW}⚠ API senaryo üretemedi, yedek senaryo kullanılıyor...{RESET}")
        scenario = FALLBACK_SCENARIO
        session_id = None

    return scenario, session_id


# ═══════════════════════════════════════════════════════════════════
#  4) HASTA İLE SOHBET + DUYGU ANALİZİ
# ═══════════════════════════════════════════════════════════════════
def test_chat(token: str, patient_profile: dict, session_id: int | None) -> tuple[list[dict], list[dict]]:
    sep("4 — HASTA SOHBET + DUYGU ANALİZİ  (POST /chat)", "💬")

    doctor_questions = [
        "Merhaba, ben doktorunuz. Bugün size nasıl yardımcı olabilirim?",
        "Bu ağrı ne zaman başladı? Tam olarak neresinde hissediyorsunuz?",
        "Daha önce böyle bir şikayetiniz oldu mu? Sürekli bir ilaç kullanıyor musunuz?",
        "Bulantı, kusma veya ishal gibi şikayetleriniz var mı?",
    ]

    chat_history: list[dict] = []
    emotion_log: list[dict] = []
    current_emotion = ""

    for i, question in enumerate(doctor_questions, 1):
        sub_sep(f"Tur {i}/{len(doctor_questions)}")
        print(f"    {YELLOW}🩺 Doktor:{RESET} {question}")

        payload = {
            "message": question,
            "history": chat_history,
            "patient_profile": patient_profile,
            "session_id": session_id,
            "emotion_state": current_emotion,
        }

        try:
            t0 = time.time()
            r = api_post("/chat", payload, token=token)
            elapsed = time.time() - t0
            data = r.json()

            if r.status_code == 200:
                reply = data.get("patient_reply", "")
                emotion = data.get("emotion")

                check(len(reply) > 10, f"Yanıt alındı ({len(reply)} karakter, {elapsed:.1f}s)", "Yanıt çok kısa")
                print(f"    {GREEN}🤒 Hasta:{RESET} {reply[:200]}{'...' if len(reply) > 200 else ''}")

                if emotion:
                    emo = emotion.get("emotion", "?")
                    intensity = emotion.get("intensity", "?")
                    check(True, f"Duygu: {emo} (şiddet: {intensity})", "")
                    current_emotion = emo
                    emotion_log.append(emotion)
                    if emotion.get("reason"):
                        print(f"    {DIM}   Sebep: {emotion['reason']}{RESET}")
                else:
                    skip("Duygu analizi döndürülmedi")

                chat_history.append({"role": "doctor", "content": question})
                chat_history.append({"role": "patient", "content": reply})
            else:
                check(False, "", f"HTTP {r.status_code}: {data}")
                break

        except Exception as exc:
            check(False, "", f"Hata: {exc}")
            break

    print(f"\n    📊 Sohbet özeti: {len(chat_history)} mesaj, {len(emotion_log)} duygu kaydı")
    return chat_history, emotion_log


# ═══════════════════════════════════════════════════════════════════
#  5) FİZİK MUAYENE
# ═══════════════════════════════════════════════════════════════════
def test_examine(token: str, patient_profile: dict) -> list[str]:
    sep("5 — FİZİK MUAYENE  (POST /examine)", "🩺")

    areas = [
        ("vital_signs", "Vital Bulgular"),
        ("general", "Genel Görünüm"),
        ("abdomen", "Karın"),
        ("chest", "Göğüs"),
    ]
    actions: list[str] = []

    for area_key, area_label in areas:
        sub_sep(f"Muayene: {area_label}")
        payload = {"area": area_key, "patient_profile": patient_profile}

        try:
            r = api_post("/examine", payload, token=token, timeout=10)
            data = r.json()

            if r.status_code == 200:
                findings = data.get("findings", "")
                check(len(findings) > 5, f"{data['area']}: {findings[:120]}", "Bulgu çok kısa")
                actions.append(f"Muayene: {data['area']}")
            else:
                check(False, "", f"HTTP {r.status_code}")
        except Exception as exc:
            check(False, "", f"Hata: {exc}")

    return actions


# ═══════════════════════════════════════════════════════════════════
#  6) TETKİK İSTEME
# ═══════════════════════════════════════════════════════════════════
def test_order_tests(token: str, patient_profile: dict) -> list[str]:
    sep("6 — TETKİK İSTEME  (POST /order_test)", "🧪")

    tests = [
        ("complete_blood_count", "Hemogram"),
        ("biochemistry", "Biyokimya"),
        ("urinalysis", "İdrar Tahlili"),
        ("ultrasound", "Ultrason"),
        ("ct_scan", "BT (Yok)"),
    ]
    actions: list[str] = []

    for test_key, test_label in tests:
        sub_sep(f"Tetkik: {test_label}")
        payload = {"test_type": test_key, "patient_profile": patient_profile}

        try:
            r = api_post("/order_test", payload, token=token, timeout=10)
            data = r.json()

            if r.status_code == 200:
                status = data.get("status", "?")
                results = data.get("results", "")
                icon = "✅" if status == "completed" else "⚠️"
                check(True, f"{icon} {data.get('test_name', test_label)} — durum: {status}", "")
                print(f"    {DIM}   {results[:150]}{RESET}")
                actions.append(f"Tetkik: {data.get('test_name', test_label)}")
            else:
                check(False, "", f"HTTP {r.status_code}")
        except Exception as exc:
            check(False, "", f"Hata: {exc}")

    return actions


# ═══════════════════════════════════════════════════════════════════
#  7) TUTOR AI — İPUCU
# ═══════════════════════════════════════════════════════════════════
def test_hint(token: str, chat_history: list[dict], actions: list[str], profile: dict) -> None:
    sep("7 — TUTOR AI: İpucu  (POST /hint)", "💡")

    payload = {
        "chat_history": chat_history,
        "actions_taken": actions,
        "patient_profile": profile,
    }

    try:
        t0 = time.time()
        r = api_post("/hint", payload, token=token, timeout=60)
        elapsed = time.time() - t0
        data = r.json()

        if r.status_code == 200:
            hint = data.get("hint", {})
            check(True, f"İpucu alındı — {elapsed:.1f}s", "")

            if isinstance(hint, dict):
                level = hint.get("hint_level", hint.get("level", "?"))
                text = hint.get("hint_text", hint.get("hint", hint.get("text", "")))
                progress = hint.get("progress_percent", hint.get("progress", "?"))

                check(bool(text), f"Seviye: {level}", "İpucu metni boş")
                print(f"    {MAGENTA}💡 İpucu:{RESET} {text}")
                print(f"    {DIM}   İlerleme: %{progress}{RESET}")
            else:
                check(bool(hint), f"İpucu: {str(hint)[:200]}", "İpucu boş")
        else:
            check(False, "", f"HTTP {r.status_code}: {data}")
    except Exception as exc:
        check(False, "", f"Hata: {exc}")


# ═══════════════════════════════════════════════════════════════════
#  8) TEDAVİ PLANI DEĞERLENDİRMESİ
# ═══════════════════════════════════════════════════════════════════
def test_treatment(token: str, patient_profile: dict) -> dict:
    sep("8 — TEDAVİ PLANI  (POST /treatment)", "💊")

    treatment_text = """
    Tedavi Planı:
    1. İlaç Tedavisi:
       - Pantoprazol 40mg tablet, günde 1 kez, aç karnına (4 hafta)
       - Sukralfat süspansiyon, günde 4 kez, yemeklerden 30dk önce (2 hafta)
    2. Yaşam Tarzı:
       - Baharatlı ve asitli gıdalardan kaçınma
       - Küçük ve sık öğünler
       - Sigara ve alkol bırakılmalı
    3. Takip:
       - 4 hafta sonra kontrol
       - Şikayetler devam ederse endoskopi planlanmalı
    """

    payload = {
        "treatment_text": treatment_text.strip(),
        "patient_profile": patient_profile,
    }

    try:
        t0 = time.time()
        r = api_post("/treatment", payload, token=token, timeout=60)
        elapsed = time.time() - t0
        data = r.json()

        if r.status_code == 200:
            te = data.get("treatment_evaluation", {})
            check(True, f"Tedavi değerlendirildi — {elapsed:.1f}s", "")

            if isinstance(te, dict):
                # Puanları göster
                score_fields = ["drug_selection", "dosage", "route_and_duration", "overall_score"]
                for field in score_fields:
                    val = te.get(field)
                    if val is not None:
                        print(f"    📊 {field}: {val}")

                # Güvenlik kontrolleri
                safety = te.get("safety_check", {})
                if isinstance(safety, dict):
                    allergy = safety.get("allergy_conflict", "?")
                    interaction = safety.get("drug_interaction", "?")
                    print(f"    🛡️  Alerji çakışması: {allergy}")
                    print(f"    🛡️  İlaç etkileşimi: {interaction}")

                comment = te.get("overall_comment", te.get("comment", ""))
                if comment:
                    print(f"    {MAGENTA}💬 Yorum:{RESET} {comment[:200]}")

                check("overall_score" in te or "score" in te or len(te) > 2,
                      f"Değerlendirme detaylı ({len(te)} alan)",
                      "Değerlendirme çok kısa")
            else:
                print(f"    {pretty(te)}")

            return te
        else:
            check(False, "", f"HTTP {r.status_code}: {data}")
            return {}
    except Exception as exc:
        check(False, "", f"Hata: {exc}")
        return {}


# ═══════════════════════════════════════════════════════════════════
#  9) HASTALIK TAHMİNİ
# ═══════════════════════════════════════════════════════════════════
def test_diagnose(token: str) -> None:
    sep("9 — HASTALIK TAHMİNİ  (POST /diagnose)", "🔬")

    payload = {
        "symptoms": "3 gündür epigastrik bölgede yanıcı ağrı, yemekle artan, antasitle azalan",
        "exam_findings": "Epigastrik hassasiyet, defans yok, rebound yok",
        "test_results": "Hemogram normal, CRP normal, USG normal",
    }
    print(f"    {YELLOW}→ Belirtiler: {payload['symptoms'][:80]}...{RESET}")

    try:
        t0 = time.time()
        r = api_post("/diagnose", payload, token=token, timeout=60)
        elapsed = time.time() - t0
        data = r.json()

        if r.status_code == 200:
            prediction = data.get("prediction", {})
            check(True, f"Tahmin alındı — {elapsed:.1f}s", "")

            if isinstance(prediction, dict):
                primary = prediction.get("primary_diagnosis", prediction.get("diagnosis", "?"))
                confidence = prediction.get("confidence", "?")
                differentials = prediction.get("differential_diagnoses", prediction.get("differentials", []))

                print(f"    🎯 Birincil tanı: {BOLD}{primary}{RESET}")
                print(f"    📊 Güven: {confidence}")
                if differentials:
                    print(f"    📋 Ayırıcı tanılar:")
                    for dd in differentials[:5]:
                        if isinstance(dd, dict):
                            print(f"       • {dd.get('diagnosis', dd.get('name', dd))}: {dd.get('probability', dd.get('confidence', ''))}")
                        else:
                            print(f"       • {dd}")
            else:
                print(f"    {pretty(prediction)}")
        else:
            check(False, "", f"HTTP {r.status_code}: {data}")
    except Exception as exc:
        check(False, "", f"Hata: {exc}")


# ═══════════════════════════════════════════════════════════════════
# 10) PERFORMANS DEĞERLENDİRMESİ + ELO/XP
# ═══════════════════════════════════════════════════════════════════
def test_evaluate(
    token: str,
    chat_history: list[dict],
    correct_diagnosis: str,
    actions: list[str],
    session_id: int | None,
    treatment: dict | None,
    emotion_log: list[dict] | None,
) -> dict | None:
    sep("10 — DEĞERLENDİRME + GAMİFİCATİON  (POST /evaluate)", "📊")

    payload = {
        "chat_history": chat_history,
        "correct_diagnosis": correct_diagnosis,
        "actions_taken": actions,
        "student_diagnosis": "Gastrit",
        "session_id": session_id,
        "treatment": treatment,
        "emotion_log": emotion_log,
    }

    print(f"    {YELLOW}→ Sohbet: {len(chat_history)} mesaj")
    print(f"    → Yapılan işlem: {len(actions)} adet")
    print(f"    → Doğru tanı: {correct_diagnosis}")
    print(f"    → Öğrenci tanısı: Gastrit")
    print(f"    → Session ID: {session_id}{RESET}")

    try:
        t0 = time.time()
        r = api_post("/evaluate", payload, token=token, timeout=90)
        elapsed = time.time() - t0
        data = r.json()

        if r.status_code == 200:
            evaluation = data.get("evaluation", {})
            session_result = data.get("session_result")

            check(True, f"Değerlendirme alındı — {elapsed:.1f}s", "")

            # Evaluation detayları
            if isinstance(evaluation, dict):
                score = evaluation.get("overall_score", evaluation.get("score", "?"))
                print(f"\n    {BOLD}📋 Değerlendirme Raporu:{RESET}")
                print(f"    {'─' * 40}")

                for key, val in evaluation.items():
                    if isinstance(val, (int, float, str)) and key != "overall_score":
                        print(f"    • {key}: {val}")

                print(f"    {'─' * 40}")
                print(f"    {BOLD}🎯 Genel Puan: {score}/100{RESET}")

            # Gamification sonuçları
            if session_result:
                check(True, "Gamification hesaplandı", "")
                print(f"\n    {BOLD}🎮 Gamification Sonuçları:{RESET}")
                print(f"    {'─' * 40}")
                elo_change = session_result.get("elo_change", 0)
                elo_after = session_result.get("elo_after", "?")
                xp_earned = session_result.get("xp_earned", 0)
                new_level = session_result.get("new_level", "?")
                new_badges = session_result.get("new_badges", [])
                diag_correct = session_result.get("diagnosis_correct", "?")

                elo_icon = "📈" if elo_change >= 0 else "📉"
                print(f"    {elo_icon} ELO: {elo_after} ({'+' if elo_change >= 0 else ''}{elo_change})")
                print(f"    ⚡ XP: +{xp_earned}")
                print(f"    🎓 Seviye: {new_level}")
                print(f"    🩺 Tanı doğru: {diag_correct}")

                if new_badges:
                    print(f"    🏅 Yeni rozetler:")
                    for badge in new_badges:
                        print(f"       🎖️  {badge}")
                else:
                    print(f"    🏅 Yeni rozet yok")

                return session_result
            else:
                skip("Gamification sonucu döndürülmedi (session_id yoksa normal)")

            return None
        else:
            check(False, "", f"HTTP {r.status_code}: {data}")
            return None
    except Exception as exc:
        check(False, "", f"Hata: {exc}")
        return None


# ═══════════════════════════════════════════════════════════════════
# 11) KULLANICI PROFİLİ
# ═══════════════════════════════════════════════════════════════════
def test_profile(token: str) -> None:
    sep("11 — KULLANICI PROFİLİ  (GET /profile)", "👤")

    try:
        r = api_get("/profile", token=token)
        data = r.json()

        if r.status_code == 200:
            check(True, "Profil alındı", f"HTTP {r.status_code}")

            # Ana istatistikler
            elo = data.get("elo_rating", data.get("elo", "?"))
            level = data.get("level", "?")
            xp = data.get("total_xp", data.get("xp", "?"))
            total = data.get("total_sessions", "?")
            streak = data.get("streak_days", data.get("streak", "?"))

            print(f"    📊 ELO Rating: {elo}")
            print(f"    🎓 Seviye: {level}")
            print(f"    ⚡ Toplam XP: {xp}")
            print(f"    📝 Toplam Oturum: {total}")
            print(f"    🔥 Seri (gün): {streak}")

            check(elo != "?" or level != "?", "İstatistikler mevcut", "Profil verileri eksik")
        else:
            check(False, "", f"HTTP {r.status_code}: {data}")
    except Exception as exc:
        check(False, "", f"Hata: {exc}")


# ═══════════════════════════════════════════════════════════════════
# 12) LİDERLİK TABLOSU
# ═══════════════════════════════════════════════════════════════════
def test_leaderboard(token: str) -> None:
    sep("12 — LİDERLİK TABLOSU  (GET /leaderboard)", "🏆")

    try:
        r = api_get("/leaderboard", token=token)
        data = r.json()

        if r.status_code == 200:
            lb = data.get("leaderboard", [])
            check(True, f"Liderlik tablosu: {len(lb)} kişi", "")

            if lb:
                print(f"\n    {'Sıra':<6}{'İsim':<25}{'ELO':<8}{'Seviye':<8}{'Oturum':<8}")
                print(f"    {'─' * 55}")
                for i, entry in enumerate(lb[:10], 1):
                    name = entry.get("name", "?")
                    elo = entry.get("elo_rating", "?")
                    level = entry.get("level", "?")
                    sessions = entry.get("total_sessions", "?")
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f" {i}"
                    print(f"    {medal:<6}{name:<25}{elo:<8}{level:<8}{sessions:<8}")
            else:
                print(f"    {DIM}(Henüz liderlik tablosunda kimse yok){RESET}")
        else:
            check(False, "", f"HTTP {r.status_code}: {data}")
    except Exception as exc:
        check(False, "", f"Hata: {exc}")


# ═══════════════════════════════════════════════════════════════════
# 13) ROZETLER
# ═══════════════════════════════════════════════════════════════════
def test_achievements(token: str) -> None:
    sep("13 — ROZETLER  (GET /achievements)", "🏅")

    try:
        r = api_get("/achievements", token=token)
        data = r.json()

        if r.status_code == 200:
            achievements = data.get("achievements", [])
            check(True, f"Rozet sayısı: {len(achievements)}", "")

            if achievements:
                for ach in achievements:
                    if isinstance(ach, dict):
                        name = ach.get("badge_name", ach.get("name", "?"))
                        earned = ach.get("earned_at", "?")
                        print(f"    🎖️  {name} — {earned}")
                    else:
                        print(f"    🎖️  {ach}")
            else:
                print(f"    {DIM}(Henüz rozet kazanılmamış — ilk oturum sonrası gelecek){RESET}")
        else:
            check(False, "", f"HTTP {r.status_code}: {data}")
    except Exception as exc:
        check(False, "", f"Hata: {exc}")


# ═══════════════════════════════════════════════════════════════════
# 14) OTURUM GEÇMİŞİ
# ═══════════════════════════════════════════════════════════════════
def test_sessions(token: str) -> None:
    sep("14 — OTURUM GEÇMİŞİ  (GET /sessions)", "📜")

    try:
        r = api_get("/sessions", token=token)
        data = r.json()

        if r.status_code == 200:
            sessions = data.get("sessions", [])
            check(True, f"Toplam oturum: {len(sessions)}", "")

            if sessions:
                print(f"\n    {'#':<4}{'Konu':<20}{'Zorluk':<10}{'Puan':<8}{'ELO Δ':<8}{'Tarih':<20}")
                print(f"    {'─' * 70}")
                for i, s in enumerate(sessions[:10], 1):
                    topic = (s.get("topic", "?"))[:18]
                    diff = s.get("difficulty", "?")
                    score = s.get("score", "-")
                    elo_c = s.get("elo_change", "-")
                    raw_date = s.get("completed_at") or s.get("started_at", "?")
                    if isinstance(raw_date, (int, float)):
                        import datetime
                        date = datetime.datetime.fromtimestamp(raw_date).strftime("%Y-%m-%d %H:%M")
                    else:
                        date = str(raw_date)[:19]
                    print(f"    {i:<4}{topic:<20}{diff:<10}{score:<8}{elo_c:<8}{date:<20}")
            else:
                print(f"    {DIM}(Henüz tamamlanmış oturum yok){RESET}")
        else:
            check(False, "", f"HTTP {r.status_code}: {data}")
    except Exception as exc:
        check(False, "", f"Hata: {exc}")


# ═══════════════════════════════════════════════════════════════════
# BONUS: HATA DAYANIKLILIĞI TESTLERİ
# ═══════════════════════════════════════════════════════════════════
def test_error_handling(token: str) -> None:
    sep("BONUS — HATA DAYANIKLILIĞI TESTLERİ", "🛡️")

    # Boş topic
    sub_sep("Boş konu ile senaryo üretimi")
    r = api_post("/generate_scenario", {"topic": "", "difficulty": "Orta"}, token=token, timeout=10)
    check(r.status_code == 422, f"Doğrulama hatası döndü (422)", f"Beklenen 422, aldık {r.status_code}")

    # Geçersiz zorluk
    sub_sep("Geçersiz zorluk seviyesi")
    r = api_post("/generate_scenario", {"topic": "test", "difficulty": "Süper"}, token=token, timeout=10)
    check(r.status_code == 422, f"Doğrulama hatası döndü (422)", f"Beklenen 422, aldık {r.status_code}")

    # Boş sohbet mesajı
    sub_sep("Boş mesaj ile sohbet")
    r = api_post("/chat", {
        "message": "",
        "history": [],
        "patient_profile": {"name": "Test"},
    }, token=token, timeout=10)
    check(r.status_code == 422, f"Doğrulama hatası döndü (422)", f"Beklenen 422, aldık {r.status_code}")

    # Kısa tedavi metni
    sub_sep("Çok kısa tedavi planı")
    r = api_post("/treatment", {
        "treatment_text": "ab",
        "patient_profile": {"name": "Test"},
    }, token=token, timeout=10)
    check(r.status_code == 422, f"Doğrulama hatası döndü (422)", f"Beklenen 422, aldık {r.status_code}")

    # Geçersiz muayene bölgesi
    sub_sep("Geçersiz muayene bölgesi")
    r = api_post("/examine", {
        "area": "böbrek",
        "patient_profile": {"name": "Test"},
    }, token=token, timeout=10)
    check(r.status_code == 422, f"Doğrulama hatası döndü (422)", f"Beklenen 422, aldık {r.status_code}")


# ═══════════════════════════════════════════════════════════════════
# ANA AKIŞ
# ═══════════════════════════════════════════════════════════════════
def main():
    total_start = time.time()

    print(f"""
{BOLD}{CYAN}
  ╔═══════════════════════════════════════════════════════════╗
  ║                                                           ║
  ║     🏥  AntrenmanAI — KAPSAMLI TEST BETİĞİ  v2.0  🏥    ║
  ║                                                           ║
  ║     14 Endpoint  ·  18 Route  ·  Tam Kapsam               ║
  ║                                                           ║
  ╚═══════════════════════════════════════════════════════════╝
{RESET}
    Hedef: {BASE_URL}
    """)

    # ── 0) Sağlık kontrolü ────────────────────────────────────────
    if not test_health():
        return

    # ── 1) Auth: Google Login ─────────────────────────────────────
    token = test_auth_login()
    if not token:
        print(f"\n{RED}❌ Token alınamadı, testler durduruluyor.{RESET}")
        return

    # ── 2) Auth: Me ───────────────────────────────────────────────
    test_auth_me(token)

    # ── 3) Senaryo üretimi (3 zorluk) ────────────────────────────
    scenario, session_id = test_generate_scenario(token)
    correct_diagnosis = scenario.get("correct_diagnosis", "Gastrit")

    # ── 4) Hasta sohbeti + duygu ──────────────────────────────────
    chat_history, emotion_log = test_chat(token, scenario, session_id)

    if not chat_history:
        print(f"{RED}⚠ Sohbet başarısız, bazı testler atlanacak.{RESET}")

    # ── 5) Fizik muayene ──────────────────────────────────────────
    exam_actions = test_examine(token, scenario)

    # ── 6) Tetkik isteme ──────────────────────────────────────────
    test_actions = test_order_tests(token, scenario)
    all_actions = exam_actions + test_actions

    # ── 7) Tutor AI ipucu ─────────────────────────────────────────
    if chat_history:
        test_hint(token, chat_history, all_actions, scenario)
    else:
        skip("Sohbet olmadan ipucu test edilemez")

    # ── 8) Tedavi planı ───────────────────────────────────────────
    treatment_eval = test_treatment(token, scenario)

    # ── 9) Hastalık tahmini ───────────────────────────────────────
    test_diagnose(token)

    # ── 10) Değerlendirme + ELO/XP ───────────────────────────────
    if chat_history:
        test_evaluate(
            token, chat_history, correct_diagnosis, all_actions,
            session_id, treatment_eval, emotion_log,
        )
    else:
        skip("Sohbet olmadan değerlendirme yapılamaz")

    # ── 11-14) Gamification endpoint'leri ─────────────────────────
    test_profile(token)
    test_leaderboard(token)
    test_achievements(token)
    test_sessions(token)

    # ── BONUS) Hata dayanıklılığı ─────────────────────────────────
    test_error_handling(token)

    # ═══════════════════════════════════════════════════════════════
    # SONUÇ
    # ═══════════════════════════════════════════════════════════════
    total_elapsed = time.time() - total_start
    total = PASS_COUNT + FAIL_COUNT + SKIP_COUNT

    print(f"""
{'━' * 64}

  {BOLD}📊 TEST SONUÇLARI{RESET}

  {GREEN}✅ Başarılı:   {PASS_COUNT}{RESET}
  {RED}❌ Başarısız:  {FAIL_COUNT}{RESET}
  {YELLOW}⏭️  Atlanan:    {SKIP_COUNT}{RESET}
  {'─' * 30}
  📝 Toplam:     {total}
  ⏱️  Süre:       {total_elapsed:.1f} saniye

{'━' * 64}""")

    if FAIL_COUNT == 0:
        print(f"""
  {GREEN}{BOLD}╔═══════════════════════════════════════════════╗
  ║   🎉  TÜM TESTLER BAŞARILI!  🎉              ║
  ╚═══════════════════════════════════════════════╝{RESET}
""")
    else:
        print(f"""
  {YELLOW}{BOLD}╔═══════════════════════════════════════════════╗
  ║   ⚠️  {FAIL_COUNT} TEST BAŞARISIZ — yukarıdaki ❌ leri incele  ║
  ╚═══════════════════════════════════════════════╝{RESET}
""")


if __name__ == "__main__":
    main()
