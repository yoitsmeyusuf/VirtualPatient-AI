import { useState } from "react";
import { Pill, Loader2, CheckCircle2, AlertTriangle } from "lucide-react";
import * as api from "../api";

function scoreColor(score) {
  if (score >= 8) return "text-green-600 bg-green-50 border-green-200";
  if (score >= 6) return "text-yellow-600 bg-yellow-50 border-yellow-200";
  return "text-red-600 bg-red-50 border-red-200";
}

export default function TreatmentPanel({ scenario, onTreatmentResult }) {
  const [treatmentText, setTreatmentText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    if (!treatmentText.trim()) return;
    setLoading(true);
    try {
      const data = await api.submitTreatment(treatmentText, scenario);
      const evaluation = data.treatment_evaluation || data;
      setResult(evaluation);
      if (onTreatmentResult) onTreatmentResult(evaluation);
    } catch (err) {
      alert("Tedavi değerlendirme hatası: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 bg-white rounded-xl border border-orange-200 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <Pill className="w-5 h-5 text-orange-500" />
        <h3 className="font-semibold text-gray-800">Tedavi Planı</h3>
      </div>

      {!result ? (
        <>
          <p className="text-xs text-gray-500 mb-3">
            Hastaya uygulanacak tedavi planını yazın (ilaç adı, doz, uygulama yolu, süre, cerrahi gereksinimi vb.)
          </p>
          <textarea
            value={treatmentText}
            onChange={(e) => setTreatmentText(e.target.value)}
            placeholder={`Örnek:\n- Amoksisilin 1g PO 2x1, 7 gün\n- Parasetamol 500mg PO gerektiğinde\n- IV sıvı: %0.9 NaCl 1000ml/gün\n- Cerrahi konsültasyon gerekli`}
            rows={5}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm
                       focus:outline-none focus:ring-2 focus:ring-orange-300 focus:border-orange-400
                       resize-none"
          />
          <button
            onClick={handleSubmit}
            disabled={loading || !treatmentText.trim()}
            className="mt-3 w-full px-4 py-2.5 bg-orange-500 text-white rounded-lg 
                       hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed 
                       transition-colors flex items-center justify-center gap-2 text-sm font-medium"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Pill className="w-4 h-4" />
            )}
            {loading ? "Değerlendiriliyor..." : "Tedavi Planını Değerlendir"}
          </button>
        </>
      ) : (
        <div className="space-y-3">
          {/* Genel skor */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Tedavi Skoru</span>
            <span className={`text-lg font-bold px-3 py-1 rounded-lg border ${scoreColor(result.treatment_score)}`}>
              {result.treatment_score}/10
            </span>
          </div>

          {/* Kategoriler */}
          {result.drug_selection && (
            <ScoreRow
              label="İlaç Seçimi"
              score={result.drug_selection.score}
              correct={result.drug_selection.correct}
              comment={result.drug_selection.comment}
            />
          )}
          {result.dosage && (
            <ScoreRow
              label="Doz"
              score={result.dosage.score}
              correct={result.dosage.correct}
              comment={result.dosage.comment}
            />
          )}
          {result.route_and_duration && (
            <ScoreRow
              label="Uygulama & Süre"
              score={result.route_and_duration.score}
              comment={result.route_and_duration.comment}
            />
          )}
          {result.safety_check && (
            <div className="p-2 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2 text-xs">
                <span className="font-medium text-gray-700">Güvenlik</span>
                {result.safety_check.allergy_conflict && (
                  <span className="px-1.5 py-0.5 bg-red-100 text-red-700 rounded text-[10px]">
                    ⚠️ Alerji Çakışması
                  </span>
                )}
                {result.safety_check.drug_interaction && (
                  <span className="px-1.5 py-0.5 bg-yellow-100 text-yellow-700 rounded text-[10px]">
                    💊 İlaç Etkileşimi
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1">{result.safety_check.comment}</p>
            </div>
          )}

          {/* Eksikler ve öneriler */}
          {result.missing_items?.length > 0 && (
            <div className="p-2 bg-red-50 rounded-lg">
              <p className="text-xs font-medium text-red-700 mb-1">Eksik Kalemler:</p>
              <ul className="text-xs text-red-600 space-y-0.5">
                {result.missing_items.map((item, i) => (
                  <li key={i}>• {item}</li>
                ))}
              </ul>
            </div>
          )}

          {result.overall_comment && (
            <p className="text-xs text-gray-600 italic border-t pt-2">{result.overall_comment}</p>
          )}

          {/* Tekrar yaz */}
          <button
            onClick={() => { setResult(null); setTreatmentText(""); }}
            className="w-full text-xs text-orange-600 hover:text-orange-700 py-1"
          >
            ✏️ Tedavi planını yeniden yaz
          </button>
        </div>
      )}
    </div>
  );
}

function ScoreRow({ label, score, correct, comment }) {
  return (
    <div className="p-2 bg-gray-50 rounded-lg">
      <div className="flex items-center justify-between text-xs mb-1">
        <span className="font-medium text-gray-700">{label}</span>
        <div className="flex items-center gap-1.5">
          {correct !== undefined && (
            correct ? (
              <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />
            ) : (
              <AlertTriangle className="w-3.5 h-3.5 text-yellow-500" />
            )
          )}
          <span className={`font-bold ${score >= 7 ? "text-green-600" : score >= 5 ? "text-yellow-600" : "text-red-600"}`}>
            {score}/10
          </span>
        </div>
      </div>
      <p className="text-xs text-gray-500">{comment}</p>
    </div>
  );
}
