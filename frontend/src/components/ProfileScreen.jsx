import { useState, useEffect } from "react";
import {
  User,
  Trophy,
  Zap,
  Target,
  Calendar,
  Flame,
  ArrowLeft,
  Award,
  TrendingUp,
  Clock,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import * as api from "../api";

export default function ProfileScreen({ onBack }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getProfile()
      .then(setStats)
      .catch((err) => console.error("Profil yüklenemedi:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!stats || !stats.user) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-500">
        <p>Henüz profil verisi yok. İlk simülasyonunuzu yapın!</p>
      </div>
    );
  }

  const user = stats.user;
  const xpPercent = ((user.xp % 500) / 500) * 100;

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-3xl mx-auto">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-6 text-sm"
        >
          <ArrowLeft className="w-4 h-4" /> Geri
        </button>

        {/* Profil Kartı */}
        <div className="card p-8 mb-6 bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50">
          <div className="flex items-center gap-5">
            {user.picture ? (
              <img src={user.picture} alt={user.name} className="w-20 h-20 rounded-2xl border-4 border-white shadow-lg" />
            ) : (
              <div className="w-20 h-20 rounded-2xl bg-indigo-100 flex items-center justify-center">
                <User className="w-10 h-10 text-indigo-400" />
              </div>
            )}
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900">{user.name || "Kullanıcı"}</h1>
              <p className="text-sm text-gray-500">{user.email}</p>
              <div className="flex items-center gap-4 mt-2">
                <span className="text-sm font-bold text-indigo-600">Seviye {user.level}</span>
                <span className="text-sm text-gray-400">|</span>
                <span className="text-sm font-bold text-amber-600">ELO {user.elo_rating}</span>
              </div>
            </div>
          </div>

          {/* XP Progress */}
          <div className="mt-5">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>Seviye {user.level}</span>
              <span>{user.xp % 500} / 500 XP</span>
              <span>Seviye {user.level + 1}</span>
            </div>
            <div className="w-full h-3 bg-white/60 rounded-full overflow-hidden">
              <div
                className="h-3 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
                style={{ width: `${xpPercent}%` }}
              />
            </div>
          </div>
        </div>

        {/* İstatistikler */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatCard icon={Target} label="Toplam Oturum" value={stats.total_sessions} color="blue" />
          <StatCard icon={CheckCircle2} label="Doğru Tanı" value={`${stats.accuracy_percent}%`} color="green" />
          <StatCard icon={TrendingUp} label="Ort. Skor" value={stats.average_score} color="purple" />
          <StatCard icon={Flame} label="Günlük Seri" value={`${stats.streak_days} gün`} color="orange" />
        </div>

        {/* Zorluk Dağılımı */}
        {stats.difficulty_distribution && (
          <div className="card p-5 mb-6">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <Zap className="w-5 h-5 text-amber-500" />
              Zorluk Dağılımı
            </h3>
            <div className="grid grid-cols-3 gap-3">
              {Object.entries(stats.difficulty_distribution).map(([level, count]) => (
                <div key={level} className={`text-center p-3 rounded-xl ${
                  level === "Kolay" ? "bg-emerald-50" : level === "Zor" ? "bg-red-50" : "bg-amber-50"
                }`}>
                  <div className="text-2xl font-bold text-gray-800">{count}</div>
                  <div className="text-xs text-gray-500">{level}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Rozetler */}
        {stats.achievements?.length > 0 && (
          <div className="card p-5 mb-6">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <Award className="w-5 h-5 text-yellow-500" />
              Rozetler ({stats.achievements.length})
            </h3>
            <div className="flex flex-wrap gap-2">
              {stats.achievements.map((badge, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-yellow-50 to-amber-50 
                             border border-amber-200 rounded-full text-sm font-medium text-amber-800"
                >
                  {badge.badge_icon} {badge.badge_name}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Son Oturumlar */}
        {stats.recent_sessions?.length > 0 && (
          <div className="card p-5">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <Clock className="w-5 h-5 text-gray-500" />
              Son Oturumlar
            </h3>
            <div className="space-y-2">
              {stats.recent_sessions.map((s, i) => (
                <div key={i} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg text-sm">
                  <span className={`w-2 h-2 rounded-full ${s.diagnosis_correct ? "bg-green-500" : "bg-red-400"}`} />
                  <span className="flex-1 font-medium text-gray-700 truncate">{s.topic}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    s.difficulty === "Kolay" ? "bg-emerald-100 text-emerald-700" :
                    s.difficulty === "Zor" ? "bg-red-100 text-red-700" :
                    "bg-amber-100 text-amber-700"
                  }`}>{s.difficulty}</span>
                  <span className="font-bold text-gray-800">{s.overall_score}/10</span>
                  <span className={`text-xs font-medium ${s.elo_change >= 0 ? "text-green-600" : "text-red-600"}`}>
                    {s.elo_change >= 0 ? `+${s.elo_change}` : s.elo_change}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }) {
  const colors = {
    blue: "bg-blue-50 text-blue-600",
    green: "bg-green-50 text-green-600",
    purple: "bg-purple-50 text-purple-600",
    orange: "bg-orange-50 text-orange-600",
  };
  return (
    <div className="card p-4 text-center">
      <Icon className={`w-6 h-6 mx-auto mb-2 ${colors[color]?.split(" ")[1] || "text-gray-500"}`} />
      <div className="text-xl font-bold text-gray-800">{value}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}
