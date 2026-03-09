import { useState, useEffect } from "react";
import { ArrowLeft, Trophy, Crown, Medal, Award } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import * as api from "../api";

const RANK_ICONS = ["👑", "🥈", "🥉"];
const ELO_TIERS = [
  { min: 2000, label: "Efsane", color: "text-purple-600 bg-purple-50" },
  { min: 1800, label: "Altın", color: "text-yellow-600 bg-yellow-50" },
  { min: 1500, label: "Gümüş", color: "text-gray-600 bg-gray-100" },
  { min: 1200, label: "Bronz", color: "text-orange-600 bg-orange-50" },
  { min: 0, label: "Başlangıç", color: "text-blue-600 bg-blue-50" },
];

function getEloTier(elo) {
  return ELO_TIERS.find((t) => elo >= t.min) || ELO_TIERS[ELO_TIERS.length - 1];
}

export default function LeaderboardScreen({ onBack }) {
  const { user } = useAuth();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getLeaderboard()
      .then((res) => setData(res.leaderboard || []))
      .catch((err) => console.error("Leaderboard yüklenemedi:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-2xl mx-auto">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-6 text-sm"
        >
          <ArrowLeft className="w-4 h-4" /> Geri
        </button>

        <div className="text-center mb-8">
          <Trophy className="w-12 h-12 text-amber-500 mx-auto mb-3" />
          <h1 className="text-2xl font-bold text-gray-900">Liderlik Tablosu</h1>
          <p className="text-gray-500 text-sm">ELO sıralamasına göre en iyi doktor adayları</p>
        </div>

        {data.length === 0 ? (
          <div className="text-center text-gray-400 py-12">
            <Medal className="w-16 h-16 mx-auto mb-3 text-gray-300" />
            <p>Henüz sıralama yok. İlk simülasyonunuzu yapın!</p>
          </div>
        ) : (
          <div className="space-y-2">
            {data.map((player, idx) => {
              const rank = idx + 1;
              const tier = getEloTier(player.elo_rating);
              const isMe = player.id === user?.sub;

              return (
                <div
                  key={player.id}
                  className={`flex items-center gap-2.5 sm:gap-4 p-3 sm:p-4 rounded-xl border transition-all ${
                    isMe
                      ? "bg-indigo-50 border-indigo-200 shadow-sm"
                      : rank <= 3
                      ? "bg-amber-50/50 border-amber-100"
                      : "bg-white border-gray-100 hover:border-gray-200"
                  }`}
                >
                  {/* Sıra */}
                  <div className="w-10 text-center flex-shrink-0">
                    {rank <= 3 ? (
                      <span className="text-2xl">{RANK_ICONS[rank - 1]}</span>
                    ) : (
                      <span className="text-lg font-bold text-gray-400">#{rank}</span>
                    )}
                  </div>

                  {/* Avatar */}
                  {player.picture ? (
                    <img
                      src={player.picture}
                      alt={player.name}
                      className="w-10 h-10 rounded-full border-2 border-white shadow-sm flex-shrink-0"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                      <span className="text-sm font-bold text-gray-500">
                        {(player.name || "?").charAt(0).toUpperCase()}
                      </span>
                    </div>
                  )}

                  {/* İsim & Tier */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`font-semibold truncate ${isMe ? "text-indigo-700" : "text-gray-800"}`}>
                        {player.name || "Anonim"}
                      </span>
                      {isMe && (
                        <span className="text-[10px] bg-indigo-200 text-indigo-700 px-1.5 py-0.5 rounded">
                          Sen
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${tier.color}`}>
                        {tier.label}
                      </span>
                      <span className="text-xs text-gray-400">
                        Lv.{player.level} • {player.total_sessions} oturum
                      </span>
                    </div>
                  </div>

                  {/* ELO */}
                  <div className="text-right flex-shrink-0">
                    <div className="text-lg sm:text-xl font-bold text-gray-900">{player.elo_rating}</div>
                    <div className="text-[10px] text-gray-400">ELO</div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
