import { useState } from "react";
import {
  ArrowLeft,
  ClipboardCheck,
  Loader2,
  Brain,
  Send,
  Lightbulb,
  Heart,
  Pill,
} from "lucide-react";
import PatientInfo from "./PatientInfo";
import ChatPanel from "./ChatPanel";
import ActionPanel from "./ActionPanel";
import TreatmentPanel from "./TreatmentPanel";
import * as api from "../api";

const EMOTION_ICONS = {
  sakin: "😌",
  endişeli: "😟",
  sinirli: "😠",
  korkmuş: "😰",
  ağlamaklı: "😢",
  güvende: "😊",
  tedirgin: "😬",
  kafası_karışık: "😵‍💫",
  rahatlamış: "😌",
};

const EMOTION_COLORS = {
  sakin: "bg-blue-100 text-blue-700 border-blue-200",
  endişeli: "bg-yellow-100 text-yellow-700 border-yellow-200",
  sinirli: "bg-red-100 text-red-700 border-red-200",
  korkmuş: "bg-purple-100 text-purple-700 border-purple-200",
  ağlamaklı: "bg-indigo-100 text-indigo-700 border-indigo-200",
  güvende: "bg-green-100 text-green-700 border-green-200",
  tedirgin: "bg-orange-100 text-orange-700 border-orange-200",
  kafası_karışık: "bg-gray-100 text-gray-700 border-gray-200",
  rahatlamış: "bg-emerald-100 text-emerald-700 border-emerald-200",
};

export default function SimulationScreen({
  scenario,
  sessionId,
  chatHistory,
  setChatHistory,
  actions,
  setActions,
  onEvaluationReady,
  onRestart,
}) {
  const [evaluating, setEvaluating] = useState(false);
  const [studentDiagnosis, setStudentDiagnosis] = useState("");
  const [diagnosisPrediction, setDiagnosisPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);

  // ── Duygu durumu ──────────────────────────────────
  const [currentEmotion, setCurrentEmotion] = useState("sakin");
  const [emotionDetail, setEmotionDetail] = useState(null);
  const [emotionLog, setEmotionLog] = useState([]);

  // ── İpucu ─────────────────────────────────────────
  const [hintData, setHintData] = useState(null);
  const [hintLoading, setHintLoading] = useState(false);

  // ── Tedavi ────────────────────────────────────────
  const [showTreatment, setShowTreatment] = useState(false);
  const [treatmentResult, setTreatmentResult] = useState(null);

  // ── Sohbet gönderimi (emotion + session entegreli) ──
  const handleChatSend = async (message) => {
    const newDoctorMsg = { role: "doctor", content: message };
    const updatedHistory = [...chatHistory, newDoctorMsg];
    setChatHistory(updatedHistory);

    try {
      const data = await api.chat(
        message,
        chatHistory,
        scenario,
        sessionId,
        currentEmotion,
      );
      const patientMsg = { role: "patient", content: data.patient_reply };
      setChatHistory([...updatedHistory, patientMsg]);

      // Duygu güncelle
      if (data.emotion) {
        setCurrentEmotion(data.emotion.emotion || "sakin");
        setEmotionDetail(data.emotion);
        setEmotionLog((prev) => [...prev, data.emotion]);
      }
    } catch (err) {
      alert("Sohbet hatası: " + err.message);
      setChatHistory(chatHistory); // rollback
    }
  };

  // ── Değerlendirme al ──────────────────────────────────
  const handleEvaluate = async () => {
    if (chatHistory.length === 0) return;

    setEvaluating(true);
    try {
      const data = await api.evaluate(
        chatHistory,
        scenario.correct_diagnosis,
        actions,
        studentDiagnosis || null,
        sessionId,
        treatmentResult,
        emotionLog,
      );
      onEvaluationReady(data.evaluation || data, data.session_result);
    } catch (err) {
      alert("Değerlendirme hatası: " + err.message);
    } finally {
      setEvaluating(false);
    }
  };

  // ── Hastalık tahmini ──────────────────────────────────
  const handlePredict = async () => {
    if (!studentDiagnosis.trim()) return;

    setPredicting(true);
    try {
      const symptoms = chatHistory
        .filter((m) => m.role === "patient")
        .map((m) => m.content)
        .join("\n");
      const examFindings = actions.filter((a) => a.startsWith("Muayene:")).join("\n");
      const testResults = actions.filter((a) => a.startsWith("Tetkik:")).join("\n");

      const data = await api.diagnose(
        symptoms || scenario.chief_complaint,
        examFindings || null,
        testResults || null,
      );
      setDiagnosisPrediction(data.prediction || data);
    } catch (err) {
      alert("Tanı tahmini hatası: " + err.message);
    } finally {
      setPredicting(false);
    }
  };

  // ── İpucu iste ────────────────────────────────────────
  const handleHint = async () => {
    setHintLoading(true);
    try {
      const data = await api.getHint(chatHistory, actions, scenario);
      setHintData(data.hint || data);
    } catch (err) {
      alert("İpucu hatası: " + err.message);
    } finally {
      setHintLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col">
      {/* Üst bar */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-100 px-4 py-3 flex items-center gap-4 flex-shrink-0">
        <button
          onClick={onRestart}
          className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors"
          title="Yeni simülasyon"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>

        <div className="flex-1 min-w-0 flex items-center gap-3">
          <h1 className="font-semibold text-gray-800 truncate">
            🏥 {scenario.patient_name}
          </h1>
          {/* Zorluk badge */}
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            scenario.difficulty_level === "Kolay" ? "bg-emerald-100 text-emerald-700" :
            scenario.difficulty_level === "Zor" ? "bg-red-100 text-red-700" :
            "bg-amber-100 text-amber-700"
          }`}>
            {scenario.difficulty_level || "Orta"}
          </span>
          {/* Duygu durumu badge */}
          <span
            className={`text-xs px-2 py-0.5 rounded-full border flex items-center gap-1 ${
              EMOTION_COLORS[currentEmotion] || EMOTION_COLORS.sakin
            }`}
            title={emotionDetail?.reason || "Hasta duygu durumu"}
          >
            <Heart className="w-3 h-3" />
            {EMOTION_ICONS[currentEmotion] || "😌"} {currentEmotion}
          </span>
        </div>

        {/* İpucu butonu */}
        <button
          onClick={handleHint}
          disabled={hintLoading || chatHistory.length === 0}
          className="flex items-center gap-1.5 px-3 py-2 bg-amber-50 text-amber-700 
                     border border-amber-200 rounded-lg hover:bg-amber-100 
                     disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
          title="Tutor'dan ipucu al"
        >
          {hintLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Lightbulb className="w-4 h-4" />
          )}
          İpucu
        </button>

        {/* Tedavi butonu */}
        <button
          onClick={() => setShowTreatment(!showTreatment)}
          className={`flex items-center gap-1.5 px-3 py-2 rounded-lg border text-sm transition-colors ${
            showTreatment
              ? "bg-orange-500 text-white border-orange-500"
              : "bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100"
          }`}
        >
          <Pill className="w-4 h-4" />
          Tedavi
        </button>

        <button
          onClick={handleEvaluate}
          disabled={evaluating || chatHistory.length === 0}
          className="btn-primary flex items-center gap-2 text-sm"
        >
          {evaluating ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <ClipboardCheck className="w-4 h-4" />
          )}
          {evaluating ? "Değerlendiriliyor..." : "Değerlendirme Al"}
        </button>
      </header>

      {/* İpucu banner */}
      {hintData && (
        <div className="mx-4 mt-2 p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-3 relative">
          <Lightbulb className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold text-amber-800">Tutor İpucu</span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                hintData.hint_level === "güçlü"
                  ? "bg-red-100 text-red-700"
                  : hintData.hint_level === "orta"
                  ? "bg-amber-100 text-amber-700"
                  : "bg-green-100 text-green-700"
              }`}>
                {hintData.hint_level}
              </span>
              {hintData.progress_percent > 0 && (
                <span className="text-[10px] text-amber-600">
                  İlerleme: %{hintData.progress_percent}
                </span>
              )}
            </div>
            <p className="text-sm text-amber-900">{hintData.hint}</p>
            {hintData.missing_areas?.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-1.5">
                {hintData.missing_areas.map((area, i) => (
                  <span key={i} className="text-[10px] bg-amber-200/50 text-amber-700 px-1.5 py-0.5 rounded">
                    {area}
                  </span>
                ))}
              </div>
            )}
          </div>
          <button
            onClick={() => setHintData(null)}
            className="text-amber-400 hover:text-amber-600 text-lg leading-none"
          >
            ×
          </button>
        </div>
      )}

      {/* Ana içerik — 3 sütun */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sol — Hasta bilgisi */}
        <aside className="w-72 flex-shrink-0 p-4 overflow-y-auto border-r border-gray-100 bg-white/40">
          <PatientInfo scenario={scenario} />

          {/* Duygu geçmişi */}
          {emotionLog.length > 0 && (
            <div className="mt-4 p-3 bg-pink-50 rounded-xl border border-pink-100">
              <h4 className="text-xs font-semibold text-pink-800 mb-2 flex items-center gap-1.5">
                <Heart className="w-3.5 h-3.5" /> Duygu Geçmişi
              </h4>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {emotionLog.slice(-5).map((e, i) => (
                  <div key={i} className="text-[10px] text-pink-700 flex items-center gap-1">
                    <span>{EMOTION_ICONS[e.emotion] || "😐"}</span>
                    <span className="font-medium">{e.emotion}</span>
                    <span className="text-pink-400">— {e.reason}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </aside>

        {/* Orta — Sohbet */}
        <main className="flex-1 p-4 min-w-0 flex flex-col">
          <div className="flex-1 min-h-0">
            <ChatPanel
              scenario={scenario}
              chatHistory={chatHistory}
              setChatHistory={setChatHistory}
              onSend={handleChatSend}
            />
          </div>

          {/* Tanı Girişi */}
          <div className="mt-3 p-4 bg-white rounded-xl border border-gray-200 shadow-sm">
            <div className="flex items-center gap-2 mb-2">
              <Brain className="w-4 h-4 text-purple-500" />
              <span className="text-sm font-semibold text-gray-700">
                Tanınızı Girin
              </span>
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={studentDiagnosis}
                onChange={(e) => setStudentDiagnosis(e.target.value)}
                placeholder="Ör: Akut apandisit, Kolesistit..."
                className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm
                         focus:outline-none focus:ring-2 focus:ring-purple-300 focus:border-purple-400"
              />
              <button
                onClick={handlePredict}
                disabled={predicting || !studentDiagnosis.trim()}
                className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 
                         disabled:opacity-50 disabled:cursor-not-allowed transition-colors
                         flex items-center gap-1.5 text-sm font-medium"
              >
                {predicting ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                AI Tahmini
              </button>
            </div>

            {/* Tahmin Sonucu */}
            {diagnosisPrediction && (
              <div className="mt-3 p-3 bg-purple-50 rounded-lg border border-purple-200">
                <div className="flex items-center gap-2 mb-2">
                  <Brain className="w-4 h-4 text-purple-600" />
                  <span className="text-sm font-semibold text-purple-800">
                    AI Tanı Tahmini
                  </span>
                  <span className="ml-auto text-xs bg-purple-200 text-purple-700 px-2 py-0.5 rounded-full">
                    Güven: {Math.round((diagnosisPrediction.confidence || 0) * 100)}%
                  </span>
                </div>
                <p className="text-sm font-medium text-purple-900 mb-2">
                  {diagnosisPrediction.primary_diagnosis}
                </p>
                {diagnosisPrediction.differential_diagnoses?.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-purple-700 font-medium mb-1">Ayırıcı Tanılar:</p>
                    <ul className="space-y-1">
                      {diagnosisPrediction.differential_diagnoses.map((dd, i) => (
                        <li key={i} className="text-xs text-purple-700 flex items-start gap-1">
                          <span className="mt-0.5">•</span>
                          <span>
                            <strong>{dd.diagnosis}</strong>
                            <span className="text-purple-500 ml-1">({dd.probability})</span>
                            {dd.reasoning && <span className="text-purple-400 ml-1">— {dd.reasoning}</span>}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {diagnosisPrediction.clinical_reasoning && (
                  <p className="mt-2 text-xs text-purple-600 italic">
                    {diagnosisPrediction.clinical_reasoning}
                  </p>
                )}
              </div>
            )}
          </div>
        </main>

        {/* Sağ — Muayene & Tetkik + Tedavi */}
        <aside className="w-80 flex-shrink-0 p-4 overflow-y-auto border-l border-gray-100 bg-white/40 space-y-4">
          <ActionPanel
            scenario={scenario}
            actions={actions}
            setActions={setActions}
          />

          {/* Tedavi paneli */}
          {showTreatment && (
            <TreatmentPanel
              scenario={scenario}
              onTreatmentResult={setTreatmentResult}
            />
          )}
        </aside>
      </div>
    </div>
  );
}
