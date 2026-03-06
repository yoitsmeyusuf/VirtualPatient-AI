"""
test_api.py — AI Hasta Mikroservisi Test Betiği
--------------------------------------------------
Sunucuya istek atarak 5 endpoint'i sırayla test eder:
  1. POST /generate_scenario  →  Senaryo üret
  2. POST /chat               →  Hasta ile sohbet (birkaç tur)
  3. POST /examine            →  Fizik muayene yap
  4. POST /order_test         →  Tetkik iste
  5. POST /evaluate           →  Performans değerlendirmesi al

Kullanım:
  1. Önce sunucuyu başlat:  python main.py
  2. Başka bir terminalde:  python test_api.py
"""

import json
import requests

BASE_URL = "http://localhost:8000"

# Renklendirme (terminal çıktısı için)
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def sep(title: str) -> None:
    print(f"\n{'═' * 60}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{'═' * 60}")


def pretty(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════
# 0) SAĞLIK KONTROLÜ
# ═══════════════════════════════════════════════════════════════
def test_health() -> bool:
    sep("0 — SAĞLIK KONTROLÜ  (GET /)")
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5)
        r.raise_for_status()
        print(f"{GREEN}✓ Sunucu çalışıyor:{RESET}")
        print(pretty(r.json()))
        return True
    except requests.ConnectionError:
        print(f"{RED}✗ Sunucuya bağlanılamadı!{RESET}")
        print(f"  → Önce sunucuyu başlat: python main.py")
        return False


# ═══════════════════════════════════════════════════════════════
# 1) SENARYO ÜRETİMİ
# ═══════════════════════════════════════════════════════════════
def test_generate_scenario() -> dict | None:
    sep("1 — SENARYO ÜRETİMİ  (POST /generate_scenario)")

    payload = {"topic": "karın ağrısı"}
    print(f"{YELLOW}→ İstek:{RESET} {pretty(payload)}")

    try:
        r = requests.post(
            f"{BASE_URL}/generate_scenario",
            json=payload,
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        scenario = data.get("scenario", {})
        print(f"{GREEN}✓ Senaryo başarıyla üretildi:{RESET}")
        print(pretty(scenario))
        return scenario

    except requests.HTTPError as exc:
        print(f"{RED}✗ HTTP Hatası ({r.status_code}):{RESET} {r.text}")
        return None
    except Exception as exc:
        print(f"{RED}✗ Hata:{RESET} {exc}")
        return None


# ═══════════════════════════════════════════════════════════════
# 2) HASTA İLE SOHBET (Birkaç tur)
# ═══════════════════════════════════════════════════════════════
def test_chat(patient_profile: dict) -> list[dict]:
    sep("2 — HASTA İLE SOHBET  (POST /chat)")

    # Doktorun soracağı test soruları
    doctor_questions = [
        "Merhaba, ben doktorunuz. Bugün nasıl hissediyorsunuz?",
        "Ağrınız ne zaman başladı?",
        "Ağrının yeri tam olarak neresi, gösterebilir misiniz?",
        "Bulantı veya kusma var mı?",
    ]

    chat_history: list[dict] = []

    for i, question in enumerate(doctor_questions, 1):
        print(f"\n{YELLOW}Doktor ({i}/{len(doctor_questions)}):{RESET} {question}")

        payload = {
            "message": question,
            "history": chat_history,
            "patient_profile": patient_profile,
        }

        try:
            r = requests.post(
                f"{BASE_URL}/chat",
                json=payload,
                timeout=120,
            )
            r.raise_for_status()
            reply = r.json().get("patient_reply", "")
            print(f"{GREEN}Hasta:{RESET} {reply}")

            # Geçmişe ekle
            chat_history.append({"role": "doctor", "content": question})
            chat_history.append({"role": "patient", "content": reply})

        except requests.HTTPError:
            print(f"{RED}✗ HTTP Hatası ({r.status_code}):{RESET} {r.text}")
            break
        except Exception as exc:
            print(f"{RED}✗ Hata:{RESET} {exc}")
            break

    print(f"\n{GREEN}✓ Sohbet tamamlandı — toplam {len(chat_history)} mesaj.{RESET}")
    return chat_history


# ═══════════════════════════════════════════════════════════════
# 3) PERFORMANS DEĞERLENDİRMESİ
# ═══════════════════════════════════════════════════════════════
def test_evaluate(
    chat_history: list[dict],
    correct_diagnosis: str,
    actions_taken: list[str] | None = None,
) -> None:
    sep("5 — DEĞERLENDİRME  (POST /evaluate)")

    payload = {
        "chat_history": chat_history,
        "correct_diagnosis": correct_diagnosis,
        "actions_taken": actions_taken or [],
    }
    print(f"{YELLOW}→ Sohbet geçmişi: {len(chat_history)} mesaj{RESET}")
    print(f"{YELLOW}→ Doğru tanı: {correct_diagnosis}{RESET}")
    print(f"{YELLOW}→ Yapılan işlemler: {len(actions_taken or [])} adet{RESET}")

    try:
        r = requests.post(
            f"{BASE_URL}/evaluate",
            json=payload,
            timeout=60,
        )
        r.raise_for_status()
        evaluation = r.json().get("evaluation", {})
        print(f"{GREEN}✓ Değerlendirme raporu:{RESET}")
        print(pretty(evaluation))

    except requests.HTTPError:
        print(f"{RED}✗ HTTP Hatası ({r.status_code}):{RESET} {r.text}")
    except Exception as exc:
        print(f"{RED}✗ Hata:{RESET} {exc}")


# ═══════════════════════════════════════════════════════════════
# YEDEK SENARYO (Dış API çalışmazsa lokal test için)
# ═══════════════════════════════════════════════════════════════
FALLBACK_SCENARIO = {
    "patient_name": "Ahmet",
    "age": 45,
    "gender": "Erkek",
    "occupation": "Muhasebeci",
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
        "abdomen": "Epigastrik bölgede palpasyonla hassasiyet mevcut. Defans ve rebound yok. Barsak sesleri normoaktif.",
        "chest": "Akciğer sesleri bilateral doğal, kalp S1-S2 ritmik, üfürüm yok.",
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
            "crp": "0.8 mg/L (normal)",
        },
        "urinalysis": "Makroskopik ve mikroskopik olarak normal.",
    },
    "imaging_results": {
        "xray": "Akciğer grafisi normal, patoloji saptanmadı.",
        "ultrasound": "Karaciğer, safra kesesi, pankreas normal. Böbreklerde patoloji yok. Serbest sıvı yok.",
        "ct_scan": None,
    },
    "correct_diagnosis": "Gastrit",
    "difficulty_level": "Kolay",
}


# ═══════════════════════════════════════════════════════════════
# 3) FİZİK MUAYENE
# ═══════════════════════════════════════════════════════════════
def test_examine(patient_profile: dict) -> list[str]:
    sep("3 — FİZİK MUAYENE  (POST /examine)")

    areas = ["vital_signs", "general", "abdomen", "chest"]
    actions: list[str] = []

    for area in areas:
        area_label = {
            "vital_signs": "Vital Bulgular",
            "general": "Genel Görünüm",
            "abdomen": "Karın",
            "chest": "Göğüs",
        }.get(area, area)

        print(f"\n{YELLOW}🩺 Muayene: {area_label}{RESET}")

        payload = {
            "area": area,
            "patient_profile": patient_profile,
        }

        try:
            r = requests.post(f"{BASE_URL}/examine", json=payload, timeout=10)
            r.raise_for_status()
            data = r.json()
            print(f"{GREEN}   Bölge: {data['area']}{RESET}")
            print(f"   Bulgular: {data['findings']}")
            actions.append(f"Muayene: {data['area']} → {data['findings']}")

        except requests.HTTPError:
            print(f"{RED}✗ HTTP Hatası ({r.status_code}):{RESET} {r.text}")
        except Exception as exc:
            print(f"{RED}✗ Hata:{RESET} {exc}")

    print(f"\n{GREEN}✓ Fizik muayene tamamlandı — {len(actions)} bölge muayene edildi.{RESET}")
    return actions


# ═══════════════════════════════════════════════════════════════
# 4) TETKİK İSTEME
# ═══════════════════════════════════════════════════════════════
def test_order_tests(patient_profile: dict) -> list[str]:
    sep("4 — TETKİK İSTEME  (POST /order_test)")

    tests = ["complete_blood_count", "biochemistry", "urinalysis", "ultrasound"]
    actions: list[str] = []

    for test_type in tests:
        test_label = {
            "complete_blood_count": "Hemogram",
            "biochemistry": "Biyokimya",
            "urinalysis": "İdrar Tahlili",
            "ultrasound": "Ultrason",
        }.get(test_type, test_type)

        print(f"\n{YELLOW}🧪 Tetkik: {test_label}{RESET}")

        payload = {
            "test_type": test_type,
            "patient_profile": patient_profile,
        }

        try:
            r = requests.post(f"{BASE_URL}/order_test", json=payload, timeout=10)
            r.raise_for_status()
            data = r.json()
            status_icon = "✓" if data["status"] == "completed" else "⚠"
            print(f"{GREEN}   {status_icon} {data['test_name']}{RESET}")
            print(f"   Sonuçlar:\n{data['results']}")
            actions.append(f"Tetkik: {data['test_name']}")

        except requests.HTTPError:
            print(f"{RED}✗ HTTP Hatası ({r.status_code}):{RESET} {r.text}")
        except Exception as exc:
            print(f"{RED}✗ Hata:{RESET} {exc}")

    print(f"\n{GREEN}✓ Tetkik istekleri tamamlandı — {len(actions)} tetkik istendi.{RESET}")
    return actions


# ═══════════════════════════════════════════════════════════════
# ANA AKIŞ
# ═══════════════════════════════════════════════════════════════
def main():
    print(f"\n{BOLD}🏥 AI Hasta Mikroservisi — Test Betiği (v0.3){RESET}")
    print(f"   Hedef: {BASE_URL}\n")

    # 0) Sağlık kontrolü
    if not test_health():
        return

    # 1) Senaryo üret (başarısız olursa yedek senaryoyu kullan)
    scenario = test_generate_scenario()

    if scenario is None:
        print(f"\n{YELLOW}⚠ Dış API çalışmadı, yedek senaryo kullanılıyor...{RESET}")
        scenario = FALLBACK_SCENARIO

    correct_diagnosis = scenario.get("correct_diagnosis", "Bilinmiyor")

    # 2) Hasta ile sohbet
    chat_history = test_chat(patient_profile=scenario)

    if not chat_history:
        print(f"{RED}✗ Sohbet geçmişi boş, geri kalan adımlar atlanıyor.{RESET}")
        return

    # 3) Fizik muayene
    exam_actions = test_examine(patient_profile=scenario)

    # 4) Tetkik isteme
    test_actions = test_order_tests(patient_profile=scenario)

    # 5) Değerlendirme (tüm aksiyonlarla birlikte)
    all_actions = exam_actions + test_actions
    test_evaluate(
        chat_history=chat_history,
        correct_diagnosis=correct_diagnosis,
        actions_taken=all_actions,
    )

    sep("TEST TAMAMLANDI ✓")


if __name__ == "__main__":
    main()
