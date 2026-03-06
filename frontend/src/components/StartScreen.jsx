import { useState } from "react";
import { Stethoscope, Loader2, Sparkles, Zap, Target, Flame } from "lucide-react";
import * as api from "../api";

const SUGGESTED_TOPICS = [
  "Karın ağrısı",
  "Göğüs ağrısı",
  "Baş ağrısı",
  "Nefes darlığı",
  "Ateş ve halsizlik",
  "Bel ağrısı",
];

const DIFFICULTY_OPTIONS = [
  { value: "Kolay", label: "Kolay", icon: Zap, color: "emerald", desc: "Klasik tablo, yardımcı hasta" },
  { value: "Orta", label: "Orta", icon: Target, color: "amber", desc: "Atipik özellikler, birden fazla tanı" },
  { value: "Zor", label: "Zor", icon: Flame, color: "red", desc: "Nadir tanı, zor hasta, karmaşık tablo" },
];

export default function StartScreen({ onScenarioReady }) {
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("Orta");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async (selectedTopic) => {
    const t = selectedTopic || topic.trim();
    if (!t) return;

    setLoading(true);
    setError(null);

    try {
      const data = await api.generateScenario(t, difficulty);
      const scenario = data.scenario || data;
      onScenarioReady(scenario, data.session_id, difficulty);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        {/* Logo & Başlık */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-500 to-medical-500 shadow-lg shadow-primary-200 mb-6">
            <Stethoscope className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AntrenmanAI
          </h1>
          <p className="text-gray-500 text-lg">
            Tıp Eğitim Simülatörü
          </p>
        </div>

        {/* Ana kart */}
        <div className="card p-8">
          {/* Zorluk Seçimi */}
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Zorluk seviyesi
          </label>
          <div className="grid grid-cols-3 gap-2 mb-5">
            {DIFFICULTY_OPTIONS.map((d) => {
              const Icon = d.icon;
              const isActive = difficulty === d.value;
              return (
                <button
                  key={d.value}
                  onClick={() => setDifficulty(d.value)}
                  disabled={loading}
                  className={`p-3 rounded-xl border-2 transition-all text-center ${
                    isActive
                      ? `border-${d.color}-400 bg-${d.color}-50 shadow-sm`
                      : "border-gray-100 bg-white hover:border-gray-200"
                  }`}
                >
                  <Icon
                    className={`w-5 h-5 mx-auto mb-1 ${
                      isActive ? `text-${d.color}-500` : "text-gray-400"
                    }`}
                  />
                  <span
                    className={`text-sm font-semibold block ${
                      isActive ? `text-${d.color}-700` : "text-gray-600"
                    }`}
                  >
                    {d.label}
                  </span>
                  <span className="text-[10px] text-gray-400 leading-tight block mt-0.5">
                    {d.desc}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Konu Girişi */}
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Klinik konu veya şikayet girin
          </label>
          <div className="flex gap-3 mb-4">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
              placeholder='Örn: "Karın ağrısı"'
              className="flex-1 px-4 py-3 rounded-xl border border-gray-200 
                         focus:border-primary-400 focus:ring-2 focus:ring-primary-100 
                         outline-none transition-all text-gray-800 placeholder:text-gray-400"
              disabled={loading}
            />
            <button
              onClick={() => handleGenerate()}
              disabled={loading || !topic.trim()}
              className="btn-primary flex items-center gap-2 whitespace-nowrap"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Sparkles className="w-5 h-5" />
              )}
              {loading ? "Üretiliyor..." : "Başla"}
            </button>
          </div>

          {/* Hızlı konu seçimi */}
          <div className="flex flex-wrap gap-2">
            {SUGGESTED_TOPICS.map((t) => (
              <button
                key={t}
                onClick={() => {
                  setTopic(t);
                  handleGenerate(t);
                }}
                disabled={loading}
                className="px-3 py-1.5 text-sm rounded-lg bg-gray-50 
                           text-gray-600 hover:bg-primary-50 hover:text-primary-700 
                           border border-gray-100 hover:border-primary-200
                           transition-all disabled:opacity-50"
              >
                {t}
              </button>
            ))}
          </div>

          {error && (
            <div className="mt-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>

        <p className="text-center text-xs text-gray-400 mt-6">
          Yapay zeka destekli hasta simülasyonu — Eğitim amaçlıdır
        </p>
      </div>
    </div>
  );
}
