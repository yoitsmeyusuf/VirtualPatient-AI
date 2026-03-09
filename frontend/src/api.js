/**
 * api.js — Backend API İletişim Modülü
 * Local: Vite proxy /api/* → http://localhost:8000/*
 * Production: Doğrudan Render backend URL'si
 * JWT token otomatik olarak header'a eklenir.
 */

const BASE = import.meta.env.VITE_API_URL || "/api";
const TOKEN_KEY = "antrenman_jwt";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

async function request(endpoint, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${endpoint}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem("antrenman_user");
    window.location.reload();
    throw new Error("Oturum süresi dolmuş, tekrar giriş yapın.");
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json();
}

/** Sağlık kontrolü */
export function healthCheck() {
  return request("/");
}

/** Senaryo üret (zorluk seviyesi parametreli) */
export function generateScenario(topic, difficulty = "Orta") {
  return request("/generate_scenario", {
    method: "POST",
    body: JSON.stringify({ topic, difficulty }),
  });
}

/** Hasta ile sohbet (duygu durumu destekli) */
export function chat(message, chatHistory, patientProfile, sessionId = null, emotionState = "") {
  return request("/chat", {
    method: "POST",
    body: JSON.stringify({
      message,
      history: chatHistory,
      patient_profile: patientProfile,
      session_id: sessionId,
      emotion_state: emotionState,
    }),
  });
}

/** Fizik muayene */
export function examine(area, patientProfile) {
  return request("/examine", {
    method: "POST",
    body: JSON.stringify({
      area,
      patient_profile: patientProfile,
    }),
  });
}

/** Tetkik isteme */
export function orderTest(testType, patientProfile) {
  return request("/order_test", {
    method: "POST",
    body: JSON.stringify({
      test_type: testType,
      patient_profile: patientProfile,
    }),
  });
}

/** Değerlendirme (session + tedavi + duygu log destekli) */
export function evaluate(chatHistory, correctDiagnosis, actionsTaken, studentDiagnosis, sessionId = null, treatment = null, emotionLog = null) {
  return request("/evaluate", {
    method: "POST",
    body: JSON.stringify({
      chat_history: chatHistory,
      correct_diagnosis: correctDiagnosis,
      actions_taken: actionsTaken,
      student_diagnosis: studentDiagnosis || null,
      session_id: sessionId,
      treatment: treatment,
      emotion_log: emotionLog,
    }),
  });
}

/** Hastalık tahmini */
export function diagnose(symptoms, examFindings, testResults) {
  return request("/diagnose", {
    method: "POST",
    body: JSON.stringify({
      symptoms,
      exam_findings: examFindings || null,
      test_results: testResults || null,
    }),
  });
}

/** Tutor ipucu */
export function getHint(chatHistory, actionsTaken, patientProfile) {
  return request("/hint", {
    method: "POST",
    body: JSON.stringify({
      chat_history: chatHistory,
      actions_taken: actionsTaken,
      patient_profile: patientProfile,
    }),
  });
}

/** Tedavi değerlendirmesi */
export function submitTreatment(treatmentText, patientProfile) {
  return request("/treatment", {
    method: "POST",
    body: JSON.stringify({
      treatment_text: treatmentText,
      patient_profile: patientProfile,
    }),
  });
}

/** Liderlik tablosu */
export function getLeaderboard() {
  return request("/leaderboard");
}

/** Kullanıcı profili & istatistikler */
export function getProfile() {
  return request("/profile");
}

/** Rozetler */
export function getAchievements() {
  return request("/achievements");
}

/** Oturum geçmişi */
export function getSessions() {
  return request("/sessions");
}
