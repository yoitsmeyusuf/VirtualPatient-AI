"""
api_services.py — OpenAI GPT-4o-mini API Servisleri
------------------------------------------------------
Tüm AI görevleri (senaryo, sohbet, değerlendirme, tanı tahmini,
duygu analizi, tutor ipucu, tedavi değerlendirmesi)
GPT-4o-mini üzerinden çalışır.
"""

import json
from openai import AsyncOpenAI, APIConnectionError, RateLimitError

from config import settings
from prompts import (
    SCENARIO_SYSTEM_PROMPT,
    EVALUATOR_SYSTEM_PROMPT,
    DIAGNOSIS_SYSTEM_PROMPT,
    EMOTION_ANALYZER_PROMPT,
    TUTOR_HINT_PROMPT,
    TREATMENT_EVAL_PROMPT,
    build_patient_system_prompt,
)

# ── OpenAI async istemci ─────────────────────────────────────────────
_client = AsyncOpenAI(
    api_key=settings.EXTERNAL_API_KEY,
    base_url=settings.EXTERNAL_API_BASE_URL,
)


# ═══════════════════════════════════════════════════════════════════════
# 1) SENARYO ÜRETİMİ
# ═══════════════════════════════════════════════════════════════════════

async def generate_scenario_from_api(topic: str, difficulty: str = "Orta") -> dict:
    """GPT-4o-mini ile hasta senaryosu üretir (zorluk seviyesi parametreli)."""
    try:
        response = await _client.chat.completions.create(
            model=settings.EXTERNAL_MODEL_NAME,
            messages=[
                {"role": "system", "content": SCENARIO_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Şu tıbbi konu için gerçekçi bir hasta senaryosu üret: "
                        f"{topic}\n\nZorluk seviyesi: {difficulty}"
                    ),
                },
            ],
            temperature=0.8,
            max_tokens=2000,
        )
        raw = response.choices[0].message.content or ""
        return _safe_parse_json(raw)

    except (APIConnectionError, ConnectionError) as exc:
        raise ConnectionError(f"Dış API'ye bağlanılamadı: {exc}") from exc
    except RateLimitError as exc:
        raise ConnectionError(f"API rate limit aşıldı: {exc}") from exc
    except Exception as exc:
        raise ValueError(f"Senaryo üretilirken hata: {exc}") from exc


# ═══════════════════════════════════════════════════════════════════════
# 2) HASTA İLE SOHBET (Eski: yerel model → Yeni: GPT-4o-mini)
# ═══════════════════════════════════════════════════════════════════════

async def chat_with_patient_api(
    message: str,
    chat_history: list[dict],
    patient_profile: dict,
    emotion_state: str = "",
) -> str:
    """
    GPT-4o-mini ile hasta cevabı üretir.

    Args:
        message: Doktorun yeni mesajı.
        chat_history: Önceki sohbet geçmişi [{role, content}, ...].
        patient_profile: Senaryo'dan gelen hasta profili.
        emotion_state: Hastanın güncel duygu durumu metni.

    Returns:
        Hastanın Türkçe yanıtı.
    """
    system_prompt = build_patient_system_prompt(patient_profile, emotion_state)

    messages = [{"role": "system", "content": system_prompt}]

    # Geçmişi OpenAI formatına çevir
    for turn in chat_history:
        role = "user" if turn.get("role") == "doctor" else "assistant"
        messages.append({"role": role, "content": turn.get("content", "")})

    # Yeni doktor mesajı
    messages.append({"role": "user", "content": message})

    try:
        response = await _client.chat.completions.create(
            model=settings.EXTERNAL_MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()

    except (APIConnectionError, ConnectionError) as exc:
        raise ConnectionError(f"Dış API'ye bağlanılamadı: {exc}") from exc
    except RateLimitError as exc:
        raise ConnectionError(f"API rate limit aşıldı: {exc}") from exc
    except Exception as exc:
        raise ValueError(f"Hasta yanıtı üretilirken hata: {exc}") from exc


# ═══════════════════════════════════════════════════════════════════════
# 3) HAKEM DEĞERLENDİRMESİ
# ═══════════════════════════════════════════════════════════════════════

async def evaluate_session_from_api(
    chat_history: list[dict],
    correct_diagnosis: str,
    actions_taken: list[str] | None = None,
    student_diagnosis: str | None = None,
) -> dict:
    """Sohbet geçmişinden doktor performans değerlendirmesi alır."""
    formatted = _format_chat_history(chat_history)

    actions_text = ""
    if actions_taken:
        actions_text = (
            "\n\n### Doktorun Aldığı Aksiyonlar\n"
            + "\n".join(f"- {a}" for a in actions_taken)
        )

    diagnosis_text = ""
    if student_diagnosis:
        diagnosis_text = f"\n\n### Öğrencinin Koyduğu Tanı\n{student_diagnosis}"

    user_content = (
        f"### Sohbet Geçmişi\n{formatted}"
        f"{actions_text}"
        f"{diagnosis_text}\n\n"
        f"### Doğru Tanı\n{correct_diagnosis}"
    )

    try:
        response = await _client.chat.completions.create(
            model=settings.EXTERNAL_MODEL_NAME,
            messages=[
                {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.4,
            max_tokens=1200,
        )
        raw = response.choices[0].message.content or ""
        return _safe_parse_json(raw)

    except (APIConnectionError, ConnectionError) as exc:
        raise ConnectionError(f"Dış API'ye bağlanılamadı: {exc}") from exc
    except RateLimitError as exc:
        raise ConnectionError(f"API rate limit aşıldı: {exc}") from exc
    except Exception as exc:
        raise ValueError(f"Değerlendirme alınırken hata: {exc}") from exc


# ═══════════════════════════════════════════════════════════════════════
# 4) HASTALIK TAHMİNİ
# ═══════════════════════════════════════════════════════════════════════

async def predict_diagnosis_from_api(
    symptoms: str,
    exam_findings: str | None = None,
    test_results: str | None = None,
) -> dict:
    """
    Belirtiler ve bulgulara göre olası tanıları tahmin eder.

    Args:
        symptoms: Hastanın belirtileri (serbest metin).
        exam_findings: Muayene bulguları (opsiyonel).
        test_results: Tetkik sonuçları (opsiyonel).

    Returns:
        Tanı tahmin raporu (JSON).
    """
    user_parts = [f"### Belirtiler\n{symptoms}"]
    if exam_findings:
        user_parts.append(f"### Muayene Bulguları\n{exam_findings}")
    if test_results:
        user_parts.append(f"### Tetkik Sonuçları\n{test_results}")

    user_content = "\n\n".join(user_parts)

    try:
        response = await _client.chat.completions.create(
            model=settings.EXTERNAL_MODEL_NAME,
            messages=[
                {"role": "system", "content": DIAGNOSIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.3,
            max_tokens=800,
        )
        raw = response.choices[0].message.content or ""
        return _safe_parse_json(raw)

    except (APIConnectionError, ConnectionError) as exc:
        raise ConnectionError(f"Dış API'ye bağlanılamadı: {exc}") from exc
    except RateLimitError as exc:
        raise ConnectionError(f"API rate limit aşıldı: {exc}") from exc
    except Exception as exc:
        raise ValueError(f"Tanı tahmini alınırken hata: {exc}") from exc


# ═══════════════════════════════════════════════════════════════════════
# 5) DUYGU ANALİZİ
# ═══════════════════════════════════════════════════════════════════════

async def analyze_emotion_api(
    doctor_message: str,
    chat_history: list[dict],
    current_emotion: str = "sakin",
) -> dict:
    """Doktorun mesajının hastanın duygu durumunu nasıl etkilediğini analiz eder."""
    formatted = _format_chat_history(chat_history[-6:])  # Son 6 mesaj yeterli
    prompt = EMOTION_ANALYZER_PROMPT.format(current_emotion=current_emotion)

    try:
        response = await _client.chat.completions.create(
            model=settings.EXTERNAL_MODEL_NAME,
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": (
                        f"### Son Sohbet\n{formatted}\n\n"
                        f"### Doktorun Yeni Mesajı\n{doctor_message}"
                    ),
                },
            ],
            temperature=0.4,
            max_tokens=300,
        )
        raw = response.choices[0].message.content or ""
        return _safe_parse_json(raw)
    except Exception:
        return {
            "emotion": current_emotion,
            "intensity": "orta",
            "reason": "Analiz yapılamadı",
            "patient_reaction_hint": "",
        }


# ═══════════════════════════════════════════════════════════════════════
# 6) TUTOR İPUCU
# ═══════════════════════════════════════════════════════════════════════

async def get_tutor_hint_api(
    chat_history: list[dict],
    actions_taken: list[str],
    patient_profile: dict,
) -> dict:
    """Öğrenciye sokratik ipucu üretir."""
    chat_summary = _format_chat_history(chat_history)
    actions_summary = "\n".join(f"- {a}" for a in actions_taken) if actions_taken else "Henüz aksiyon alınmadı."

    prompt = TUTOR_HINT_PROMPT.format(
        chief_complaint=patient_profile.get("chief_complaint", "?"),
        correct_diagnosis=patient_profile.get("correct_diagnosis", "?"),
        chat_summary=chat_summary,
        actions_summary=actions_summary,
    )

    try:
        response = await _client.chat.completions.create(
            model=settings.EXTERNAL_MODEL_NAME,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Öğrenci takıldı, bir ipucu ver."},
            ],
            temperature=0.6,
            max_tokens=400,
        )
        raw = response.choices[0].message.content or ""
        return _safe_parse_json(raw)
    except Exception as exc:
        return {
            "hint": "Hastanın şikayetlerini daha detaylı sormayı dene.",
            "hint_level": "hafif",
            "missing_areas": [],
            "progress_percent": 0,
        }


# ═══════════════════════════════════════════════════════════════════════
# 7) TEDAVİ DEĞERLENDİRMESİ
# ═══════════════════════════════════════════════════════════════════════

async def evaluate_treatment_api(
    student_treatment: str,
    patient_profile: dict,
) -> dict:
    """Öğrencinin tedavi planını değerlendirir."""
    prompt = TREATMENT_EVAL_PROMPT.format(
        patient_name=patient_profile.get("patient_name", "?"),
        age=patient_profile.get("age", "?"),
        gender=patient_profile.get("gender", "?"),
        correct_diagnosis=patient_profile.get("correct_diagnosis", "?"),
        correct_treatment=patient_profile.get("correct_treatment", "Belirtilmedi"),
        allergies=", ".join(patient_profile.get("allergies", [])) or "Yok",
        medications=", ".join(patient_profile.get("medications", [])) or "Yok",
        student_treatment=student_treatment,
    )

    try:
        response = await _client.chat.completions.create(
            model=settings.EXTERNAL_MODEL_NAME,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Bu tedavi planını değerlendir."},
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        raw = response.choices[0].message.content or ""
        return _safe_parse_json(raw)
    except (APIConnectionError, ConnectionError) as exc:
        raise ConnectionError(f"Dış API'ye bağlanılamadı: {exc}") from exc
    except RateLimitError as exc:
        raise ConnectionError(f"API rate limit aşıldı: {exc}") from exc
    except Exception as exc:
        raise ValueError(f"Tedavi değerlendirmesi alınırken hata: {exc}") from exc


# ═══════════════════════════════════════════════════════════════════════
# YARDIMCI FONKSİYONLAR
# ═══════════════════════════════════════════════════════════════════════

def _safe_parse_json(text: str) -> dict:
    """Metinden güvenli şekilde JSON ayrıştırır (markdown blok + regex desteği)."""
    import re

    cleaned = text.strip()

    # 1) Direkt dene
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 2) Markdown code fence temizle: ```json ... ``` veya ``` ... ```
    fence_match = re.search(r'```(?:json)?\s*\n(.*?)```', cleaned, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3) İlk { ile son } arasını bul (metin öncesi/sonrası olabilir)
    first_brace = cleaned.find('{')
    last_brace = cleaned.rfind('}')
    if first_brace != -1 and last_brace > first_brace:
        candidate = cleaned[first_brace:last_brace + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 4) İlk [ ile son ] arasını dene (array yanıt)
    first_bracket = cleaned.find('[')
    last_bracket = cleaned.rfind(']')
    if first_bracket != -1 and last_bracket > first_bracket:
        candidate = cleaned[first_bracket:last_bracket + 1]
        try:
            result = json.loads(candidate)
            return {"items": result} if isinstance(result, list) else result
        except json.JSONDecodeError:
            pass

    # 5) Hiçbiri işe yaramadı
    raise ValueError(
        f"API'den geçerli JSON alınamadı.\nHam yanıt: {text[:500]}"
    )


def _format_chat_history(history: list[dict]) -> str:
    """Sohbet geçmişini okunabilir düz metne dönüştürür."""
    lines: list[str] = []
    for turn in history:
        role = turn.get("role", "?")
        content = turn.get("content", "")
        label = "Doktor" if role == "doctor" else "Hasta"
        lines.append(f"{label}: {content}")
    return "\n".join(lines)
