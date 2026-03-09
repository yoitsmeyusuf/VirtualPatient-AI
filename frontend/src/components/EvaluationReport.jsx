import {
  ArrowLeft,
  Trophy,
  Target,
  TrendingUp,
  AlertCircle,
  Star,
  CheckCircle2,
  XCircle,
  Award,
  Zap,
  TrendingDown,
} from "lucide-react";

const CATEGORY_LABELS = {
  history_taking: { label: "Anamnez Alma", icon: "📋" },
  physical_examination: { label: "Fizik Muayene", icon: "🩺" },
  diagnostic_workup: { label: "Tanısal İşlemler", icon: "🧪" },
  clinical_reasoning: { label: "Klinik Muhakeme", icon: "🧠" },
  communication_skills: { label: "İletişim Becerileri", icon: "💬" },
  professionalism: { label: "Profesyonellik", icon: "⭐" },
};

function scoreColor(score) {
  if (score >= 8) return "text-green-600 bg-green-50 border-green-200";
  if (score >= 6) return "text-yellow-600 bg-yellow-50 border-yellow-200";
  return "text-red-600 bg-red-50 border-red-200";
}

function scoreBg(score) {
  if (score >= 8) return "bg-green-500";
  if (score >= 6) return "bg-yellow-500";
  return "bg-red-500";
}

export default function EvaluationReport({
  evaluation,
  scenario,
  sessionResult,
  onRestart,
}) {
  if (!evaluation) return null;

  const overall = evaluation.overall_score || 0;
  const categories = evaluation.categories || {};
  const diagnosisReached = evaluation.diagnosis_reached;

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Geri düğmesi */}
        <button
          onClick={onRestart}
          className="flex items-center gap-2 text-gray-500 hover:text-gray-700 
                     mb-6 transition-colors text-sm"
        >
          <ArrowLeft className="w-4 h-4" /> Yeni Simülasyon
        </button>

        {/* Gamification Sonuçları */}
        {sessionResult && (
          <div className="card p-4 sm:p-6 mb-4 sm:mb-6 bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 border-indigo-200">
            <div className="flex items-center gap-3 mb-4">
              <Award className="w-6 h-6 text-indigo-600" />
              <h2 className="text-lg font-bold text-indigo-900">Oturum Sonuçları</h2>
            </div>
            <div className="grid grid-cols-2 gap-3 sm:gap-4">
              {/* ELO Değişimi */}
              <div className="text-center p-2 sm:p-3 bg-white/60 rounded-xl">
                <div className={`text-xl sm:text-2xl font-bold ${sessionResult.elo_change >= 0 ? "text-green-600" : "text-red-600"}`}>
                  {sessionResult.elo_change >= 0 ? (
                    <span className="flex items-center justify-center gap-1">
                      <TrendingUp className="w-5 h-5" />+{sessionResult.elo_change}
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-1">
                      <TrendingDown className="w-5 h-5" />{sessionResult.elo_change}
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-1">ELO Değişimi</p>
              </div>

              {/* XP Kazanılan */}
              <div className="text-center p-2 sm:p-3 bg-white/60 rounded-xl">
                <div className="text-xl sm:text-2xl font-bold text-amber-600 flex items-center justify-center gap-1">
                  <Zap className="w-5 h-5" />+{sessionResult.xp_earned}
                </div>
                <p className="text-xs text-gray-500 mt-1">XP Kazanıldı</p>
              </div>

              {/* Tanı */}
              <div className="text-center p-2 sm:p-3 bg-white/60 rounded-xl">
                {sessionResult.diagnosis_correct ? (
                  <CheckCircle2 className="w-8 h-8 text-green-500 mx-auto" />
                ) : (
                  <XCircle className="w-8 h-8 text-red-400 mx-auto" />
                )}
                <p className="text-xs text-gray-500 mt-1">
                  {sessionResult.diagnosis_correct ? "Doğru Tanı ✓" : "Yanlış Tanı ✗"}
                </p>
              </div>

              {/* Skor */}
              <div className="text-center p-2 sm:p-3 bg-white/60 rounded-xl">
                <div className="text-xl sm:text-2xl font-bold text-indigo-600">{sessionResult.overall_score}/10</div>
                <p className="text-xs text-gray-500 mt-1">Genel Skor</p>
              </div>
            </div>

            {/* Yeni Rozetler */}
            {sessionResult.new_badges?.length > 0 && (
              <div className="mt-4 p-3 bg-white/60 rounded-xl">
                <p className="text-sm font-semibold text-indigo-800 mb-2">🎉 Yeni Rozetler Kazandınız!</p>
                <div className="flex flex-wrap gap-2">
                  {sessionResult.new_badges.map((badge, i) => (
                    <span
                      key={i}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-yellow-100 to-amber-100 
                                 border border-amber-200 rounded-full text-sm font-medium text-amber-800 shadow-sm"
                    >
                      {badge.icon} {badge.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Genel skor kartı */}
        <div className="card p-5 sm:p-8 mb-4 sm:mb-6 text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-gradient-to-br from-primary-500 to-medical-500 text-white mb-3 sm:mb-4">
            <span className="text-3xl sm:text-4xl font-bold">{overall}</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-800 mb-1">
            Değerlendirme Raporu
          </h1>
          <p className="text-gray-500">
            {scenario?.patient_name} — {scenario?.correct_diagnosis}
          </p>

          {/* Tanı durumu */}
          <div className="mt-4 flex items-center justify-center gap-2">
            {diagnosisReached ? (
              <span className="badge bg-green-100 text-green-700 py-1.5 px-4 text-sm">
                <CheckCircle2 className="w-4 h-4 mr-1.5 inline" />
                Doğru Tanıya Ulaşıldı
              </span>
            ) : (
              <span className="badge bg-red-100 text-red-700 py-1.5 px-4 text-sm">
                <XCircle className="w-4 h-4 mr-1.5 inline" />
                Tanıya Ulaşılamadı
              </span>
            )}
          </div>

          {evaluation.student_diagnosis && (
            <p className="mt-2 text-sm text-gray-500">
              Öğrenci tanısı:{" "}
              <span className="font-medium text-gray-700">
                {evaluation.student_diagnosis}
              </span>
            </p>
          )}
        </div>

        {/* Kategori skorları */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mb-4 sm:mb-6">
          {Object.entries(categories).map(([key, cat]) => {
            const meta = CATEGORY_LABELS[key] || {
              label: key,
              icon: "📊",
            };
            return (
              <div key={key} className="card p-4 sm:p-5">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-xl">{meta.icon}</span>
                  <h3 className="font-semibold text-gray-800 flex-1">
                    {meta.label}
                  </h3>
                  <span
                    className={`text-lg font-bold px-3 py-1 rounded-lg border ${scoreColor(
                      cat.score
                    )}`}
                  >
                    {cat.score}/10
                  </span>
                </div>
                {/* Progress bar */}
                <div className="w-full h-2 bg-gray-100 rounded-full mb-3">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${scoreBg(
                      cat.score
                    )}`}
                    style={{ width: `${cat.score * 10}%` }}
                  />
                </div>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {cat.comment}
                </p>
              </div>
            );
          })}
        </div>

        {/* Güçlü yönler & Gelişim alanları */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mb-4 sm:mb-6">
          <div className="card p-4 sm:p-5">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-500" />
              Güçlü Yönler
            </h3>
            <ul className="space-y-2">
              {(evaluation.strengths || []).map((s, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
                  <Star className="w-4 h-4 text-yellow-400 flex-shrink-0" />
                  {s}
                </li>
              ))}
            </ul>
          </div>
          <div className="card p-4 sm:p-5">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <Target className="w-5 h-5 text-orange-500" />
              Gelişim Alanları
            </h3>
            <ul className="space-y-2">
              {(evaluation.areas_for_improvement || []).map((a, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
                  <AlertCircle className="w-4 h-4 text-orange-400 flex-shrink-0" />
                  {a}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Özet */}
        {evaluation.summary && (
          <div className="card p-4 sm:p-6 mb-6 sm:mb-8">
            <h3 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
              <Trophy className="w-5 h-5 text-primary-500" />
              Genel Değerlendirme
            </h3>
            <p className="text-gray-600 leading-relaxed text-sm">
              {evaluation.summary}
            </p>
          </div>
        )}

        {/* Yeniden başla */}
        <div className="text-center pb-8">
          <button onClick={onRestart} className="btn-primary text-base sm:text-lg px-6 sm:px-8 py-2.5 sm:py-3">
            🔄 Yeni Simülasyon Başlat
          </button>
        </div>
      </div>
    </div>
  );
}
