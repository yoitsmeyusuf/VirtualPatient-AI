"""
main.py — FastAPI Giriş Noktası (GPT-4o-mini + Google Auth)
---------------------------------------------------------------
Tüm AI görevleri GPT-4o-mini üzerinden çalışır.
Google OAuth + JWT ile kimlik doğrulama.

Endpoint'ler:
  POST /auth/google        →  Google ile giriş
  GET  /auth/me            →  Kullanıcı bilgisi
  POST /generate_scenario  →  Senaryo üretimi
  POST /chat               →  Hasta ile sohbet
  POST /examine            →  Fizik muayene bulguları
  POST /order_test         →  Laboratuvar / görüntüleme sonuçları
  POST /evaluate           →  Performans değerlendirmesi
  POST /diagnose           →  Hastalık tahmini
"""

import asyncio
import os
from contextlib import asynccontextmanager
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import settings
from auth import verify_google_token, create_jwt, get_current_user
from database import (
    init_db, upsert_user, get_user, get_leaderboard,
    create_session, update_session_chat, complete_session,
    get_user_sessions, get_user_achievements, get_user_stats,
)
from api_services import (
    generate_scenario_from_api,
    chat_with_patient_api,
    evaluate_session_from_api,
    predict_diagnosis_from_api,
    analyze_emotion_api,
    get_tutor_hint_api,
    evaluate_treatment_api,
)


# ═══════════════════════════════════════════════════════════════════════
# FASTAPI UYGULAMASI
# ═══════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlangıcında veritabanını hazırla."""
    await init_db()
    yield


app = FastAPI(
    title="AntrenmanAI — Tıp Eğitim Simülatörü",
    description=(
        "GPT-4o-mini tabanlı tıp eğitim simülasyonu.\n\n"
        "- **Hasta Aktör:** Doğal Türkçe hasta sohbeti + duygu modeli\n"
        "- **Senaryo Üretimi:** Zorluk seviyeli klinik senaryolar\n"
        "- **Değerlendirme:** Kapsamlı performans analizi\n"
        "- **Tanı Tahmini:** AI destekli hastalık tahmini\n"
        "- **Tedavi Planlama:** Reçete/tedavi değerlendirmesi\n"
        "- **Tutor AI:** Sokratik ipucu sistemi\n"
        "- **Gamification:** ELO rating + XP + rozetler\n"
        "- **Google Auth:** Güvenli giriş sistemi"
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────
# Production'da CORS_ORIGINS env ile ek origin eklenebilir
_extra_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        *_extra_origins,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════
# PYDANTIC MODELLERİ
# ═══════════════════════════════════════════════════════════════════════

# ── Auth ─────────────────────────────────────────────────────────────

class GoogleLoginRequest(BaseModel):
    credential: str = Field(..., description="Google ID token")


class AuthResponse(BaseModel):
    token: str
    user: dict


# ── Senaryo ──────────────────────────────────────────────────────────

class DifficultyLevel(str, Enum):
    kolay = "Kolay"
    orta = "Orta"
    zor = "Zor"


class ScenarioRequest(BaseModel):
    topic: str = Field(..., min_length=2, examples=["karın ağrısı"])
    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.orta, description="Zorluk seviyesi"
    )


class ScenarioResponse(BaseModel):
    scenario: dict
    session_id: int | None = None


# ── Sohbet ───────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., examples=["doctor", "patient"])
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)
    patient_profile: dict
    session_id: int | None = None
    emotion_state: str = ""


class ChatResponse(BaseModel):
    patient_reply: str
    emotion: dict | None = None


# ── Muayene ──────────────────────────────────────────────────────────

class ExamArea(str, Enum):
    vital_signs = "vital_signs"
    general = "general"
    abdomen = "abdomen"
    chest = "chest"
    head_neck = "head_neck"
    extremities = "extremities"
    neurological = "neurological"
    other = "other"


class ExamRequest(BaseModel):
    area: ExamArea
    patient_profile: dict


class ExamResponse(BaseModel):
    area: str
    findings: str


# ── Tetkik ───────────────────────────────────────────────────────────

class TestCategory(str, Enum):
    complete_blood_count = "complete_blood_count"
    biochemistry = "biochemistry"
    urinalysis = "urinalysis"
    xray = "xray"
    ultrasound = "ultrasound"
    ct_scan = "ct_scan"


class OrderTestRequest(BaseModel):
    test_type: TestCategory
    patient_profile: dict


class OrderTestResponse(BaseModel):
    test_name: str
    results: str
    status: str = "completed"


# ── Değerlendirme ───────────────────────────────────────────────────

class EvaluateRequest(BaseModel):
    chat_history: list[ChatMessage] = Field(..., min_length=1)
    actions_taken: list[str] = Field(default_factory=list)
    correct_diagnosis: str = Field(..., min_length=2)
    student_diagnosis: str | None = Field(
        default=None,
        description="Öğrencinin koyduğu tanı (opsiyonel).",
    )
    session_id: int | None = None
    treatment: dict | None = None
    emotion_log: list | None = None


class EvaluateResponse(BaseModel):
    evaluation: dict
    session_result: dict | None = None


# ── Tanı Tahmini ─────────────────────────────────────────────────────

class DiagnoseRequest(BaseModel):
    symptoms: str = Field(..., min_length=5, description="Hasta belirtileri")
    exam_findings: str | None = Field(default=None)
    test_results: str | None = Field(default=None)


class DiagnoseResponse(BaseModel):
    prediction: dict


# ── İpucu ────────────────────────────────────────────────────────────

class HintRequest(BaseModel):
    chat_history: list[ChatMessage] = Field(default_factory=list)
    actions_taken: list[str] = Field(default_factory=list)
    patient_profile: dict


class HintResponse(BaseModel):
    hint: dict


# ── Tedavi ───────────────────────────────────────────────────────────

class TreatmentRequest(BaseModel):
    treatment_text: str = Field(..., min_length=5, description="Tedavi planı")
    patient_profile: dict


class TreatmentResponse(BaseModel):
    treatment_evaluation: dict


# ═══════════════════════════════════════════════════════════════════════
# AUTH ENDPOINT'LERİ
# ═══════════════════════════════════════════════════════════════════════

@app.post("/auth/google", response_model=AuthResponse, tags=["Auth"])
async def google_login(request: GoogleLoginRequest):
    """Google ID token ile giriş yapar, JWT döner, DB'ye kaydeder."""
    user_info = await verify_google_token(request.credential)
    try:
        await upsert_user(user_info)
    except Exception:
        pass  # DB hatası login'i engellemez
    token = create_jwt(user_info)
    return AuthResponse(token=token, user=user_info)


@app.get("/auth/me", tags=["Auth"])
async def get_me(user: dict = Depends(get_current_user)):
    """JWT'den kullanıcı bilgisini döner."""
    return {"user": user}


# ═══════════════════════════════════════════════════════════════════════
# SAĞLIK KONTROLÜ (auth gerekmiyor)
# ═══════════════════════════════════════════════════════════════════════

@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "AntrenmanAI",
        "version": "1.0.0",
        "model": settings.EXTERNAL_MODEL_NAME,
    }


# ═══════════════════════════════════════════════════════════════════════
# KORUNALI ENDPOINT'LER (JWT gerekli)
# ═══════════════════════════════════════════════════════════════════════

# ── 1) Senaryo Üretimi ──────────────────────────────────────────────

@app.post(
    "/generate_scenario",
    response_model=ScenarioResponse,
    tags=["Senaryo"],
)
async def generate_scenario(
    request: ScenarioRequest,
    user: dict = Depends(get_current_user),
):
    """Tıbbi konuya ve zorluk seviyesine uygun hasta senaryosu üretir."""
    try:
        difficulty = request.difficulty.value
        scenario = await generate_scenario_from_api(request.topic, difficulty)

        # DB'de oturum oluştur
        session_id = None
        try:
            session_id = await create_session(
                user_id=user["sub"],
                topic=request.topic,
                difficulty=difficulty,
                scenario=scenario,
            )
        except Exception:
            pass  # DB hatası simülasyonu engellemez

        return ScenarioResponse(scenario=scenario, session_id=session_id)
    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── 2) Hasta ile Sohbet (GPT-4o-mini) ───────────────────────────────

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(
    request: ChatRequest,
    user: dict = Depends(get_current_user),
):
    """GPT-4o-mini ile hasta yanıtı üretir + duygu analizi yapar."""
    try:
        history_dicts = [msg.model_dump() for msg in request.history]
        current_emotion = request.emotion_state or "sakin"

        # Hasta yanıtı + duygu analizi paralel çalışır
        patient_reply, emotion = await asyncio.gather(
            chat_with_patient_api(
                message=request.message,
                chat_history=history_dicts,
                patient_profile=request.patient_profile,
                emotion_state=request.emotion_state,
            ),
            analyze_emotion_api(
                doctor_message=request.message,
                chat_history=history_dicts,
                current_emotion=current_emotion,
            ),
        )

        # Session güncelle
        if request.session_id:
            try:
                new_history = history_dicts + [
                    {"role": "doctor", "content": request.message},
                    {"role": "patient", "content": patient_reply},
                ]
                await update_session_chat(request.session_id, new_history, [])
            except Exception:
                pass

        return ChatResponse(patient_reply=patient_reply, emotion=emotion)
    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── 3) Fizik Muayene ────────────────────────────────────────────────

@app.post("/examine", response_model=ExamResponse, tags=["Muayene & Tetkik"])
async def examine_patient(
    request: ExamRequest,
    user: dict = Depends(get_current_user),
):
    """Senaryodaki fizik muayene bulgularını döndürür."""
    try:
        profile = request.patient_profile
        area = request.area.value

        if area == "vital_signs":
            vitals = profile.get("vital_signs", {})
            if isinstance(vitals, dict) and vitals:
                lines = [f"  {k}: {v}" for k, v in vitals.items()]
                findings = "Vital bulgular:\n" + "\n".join(lines)
            else:
                findings = "Vital bulgular henüz ölçülmedi."
            return ExamResponse(area="Vital Bulgular", findings=findings)

        exam = profile.get("physical_exam_findings", {})
        if isinstance(exam, str):
            findings = exam if exam else "Bu bölgede özellik saptanmadı."
        elif isinstance(exam, dict):
            findings = exam.get(area, "Bu bölgede özellik saptanmadı.")
        else:
            findings = "Bu bölgede özellik saptanmadı."

        area_labels = {
            "general": "Genel Görünüm",
            "abdomen": "Karın Muayenesi",
            "chest": "Göğüs Muayenesi",
            "head_neck": "Baş-Boyun Muayenesi",
            "extremities": "Ekstremite Muayenesi",
            "neurological": "Nörolojik Muayene",
            "other": "Diğer Bulgular",
        }

        return ExamResponse(
            area=area_labels.get(area, area),
            findings=findings,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── 4) Tetkik İsteme ────────────────────────────────────────────────

@app.post(
    "/order_test",
    response_model=OrderTestResponse,
    tags=["Muayene & Tetkik"],
)
async def order_test(
    request: OrderTestRequest,
    user: dict = Depends(get_current_user),
):
    """Senaryodaki tetkik sonuçlarını döndürür."""
    try:
        profile = request.patient_profile
        test_type = request.test_type.value

        test_labels = {
            "complete_blood_count": "Tam Kan Sayımı (Hemogram)",
            "biochemistry": "Biyokimya Paneli",
            "urinalysis": "İdrar Tahlili",
            "xray": "Röntgen (X-Ray)",
            "ultrasound": "Ultrasonografi",
            "ct_scan": "Bilgisayarlı Tomografi (BT)",
        }

        if test_type in ("complete_blood_count", "biochemistry", "urinalysis"):
            lab = profile.get("lab_results", {})
            if not lab:
                return OrderTestResponse(
                    test_name=test_labels[test_type],
                    results="Tetkik sonuçları bu senaryoda tanımlanmamış.",
                    status="not_available",
                )
            result_data = lab.get(test_type, {})
            if isinstance(result_data, dict) and result_data:
                lines = [f"  {k}: {v}" for k, v in result_data.items()]
                results = "\n".join(lines)
            elif isinstance(result_data, str) and result_data:
                results = result_data
            else:
                results = "Sonuç mevcut değil."

        elif test_type in ("xray", "ultrasound", "ct_scan"):
            imaging = profile.get("imaging_results", {})
            if not imaging:
                return OrderTestResponse(
                    test_name=test_labels[test_type],
                    results="Görüntüleme sonuçları tanımlanmamış.",
                    status="not_available",
                )
            result_data = imaging.get(test_type)
            results = result_data if result_data else "Çekilmedi / mevcut değil."
        else:
            results = "Bilinmeyen tetkik türü."

        return OrderTestResponse(
            test_name=test_labels.get(test_type, test_type),
            results=results,
            status="completed"
            if results and "mevcut değil" not in results
            else "not_available",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── 5) Performans Değerlendirmesi ────────────────────────────────────

@app.post("/evaluate", response_model=EvaluateResponse, tags=["Değerlendirme"])
async def evaluate_session_endpoint(
    request: EvaluateRequest,
    user: dict = Depends(get_current_user),
):
    """Doktor performansını değerlendirir ve oturumu tamamlar."""
    try:
        history_dicts = [msg.model_dump() for msg in request.chat_history]
        evaluation = await evaluate_session_from_api(
            chat_history=history_dicts,
            correct_diagnosis=request.correct_diagnosis,
            actions_taken=request.actions_taken,
            student_diagnosis=request.student_diagnosis,
        )

        # Session varsa tamamla → ELO + XP + rozet hesapla
        session_result = None
        if request.session_id:
            try:
                result = await complete_session(
                    session_id=request.session_id,
                    user_id=user["sub"],
                    evaluation=evaluation,
                    student_diagnosis=request.student_diagnosis,
                    treatment=request.treatment,
                    emotion_log=request.emotion_log,
                )
                session_result = result.get("session_result")
            except Exception:
                pass

        return EvaluateResponse(
            evaluation=evaluation, session_result=session_result
        )
    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── 6) Hastalık Tahmini ─────────────────────────────────────────────

@app.post("/diagnose", response_model=DiagnoseResponse, tags=["Tanı Tahmini"])
async def diagnose(
    request: DiagnoseRequest,
    user: dict = Depends(get_current_user),
):
    """Belirtiler ve bulgulara göre olası tanıları tahmin eder."""
    try:
        prediction = await predict_diagnosis_from_api(
            symptoms=request.symptoms,
            exam_findings=request.exam_findings,
            test_results=request.test_results,
        )
        return DiagnoseResponse(prediction=prediction)
    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ═══════════════════════════════════════════════════════════════════════
# YENİ ENDPOINT'LER (Tutor, Tedavi, Gamification)
# ═══════════════════════════════════════════════════════════════════════


# ── 7) İpucu (Tutor AI) ─────────────────────────────────────────────

@app.post("/hint", response_model=HintResponse, tags=["Tutor"])
async def get_hint(
    request: HintRequest,
    user: dict = Depends(get_current_user),
):
    """Öğrenciye sokratik ipucu üretir."""
    try:
        history_dicts = [msg.model_dump() for msg in request.chat_history]
        hint = await get_tutor_hint_api(
            chat_history=history_dicts,
            actions_taken=request.actions_taken,
            patient_profile=request.patient_profile,
        )
        return HintResponse(hint=hint)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── 8) Tedavi Değerlendirmesi ────────────────────────────────────────

@app.post("/treatment", response_model=TreatmentResponse, tags=["Tedavi"])
async def evaluate_treatment_endpoint(
    request: TreatmentRequest,
    user: dict = Depends(get_current_user),
):
    """Öğrencinin tedavi planını değerlendirir."""
    try:
        result = await evaluate_treatment_api(
            student_treatment=request.treatment_text,
            patient_profile=request.patient_profile,
        )
        return TreatmentResponse(treatment_evaluation=result)
    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── 9) Liderlik Tablosu ─────────────────────────────────────────────

@app.get("/leaderboard", tags=["Gamification"])
async def leaderboard(user: dict = Depends(get_current_user)):
    """ELO sıralamasına göre liderlik tablosu."""
    try:
        data = await get_leaderboard(limit=20)
        return {"leaderboard": data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── 10) Kullanıcı Profili ───────────────────────────────────────────

@app.get("/profile", tags=["Gamification"])
async def user_profile(user: dict = Depends(get_current_user)):
    """Giriş yapmış kullanıcının detaylı istatistikleri."""
    try:
        stats = await get_user_stats(user["sub"])
        return stats
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── 11) Rozetler ────────────────────────────────────────────────────

@app.get("/achievements", tags=["Gamification"])
async def user_achievements(user: dict = Depends(get_current_user)):
    """Kullanıcının kazandığı rozetler."""
    try:
        data = await get_user_achievements(user["sub"])
        return {"achievements": data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── 12) Oturum Geçmişi ──────────────────────────────────────────────

@app.get("/sessions", tags=["Gamification"])
async def sessions_history(user: dict = Depends(get_current_user)):
    """Kullanıcının geçmiş oturumları."""
    try:
        data = await get_user_sessions(user["sub"])
        return {"sessions": data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ═══════════════════════════════════════════════════════════════════════
# DOĞRUDAN ÇALIŞTIRMA
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True,
    )
