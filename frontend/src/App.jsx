import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginScreen from "./components/LoginScreen";
import StartScreen from "./components/StartScreen";
import SimulationScreen from "./components/SimulationScreen";
import EvaluationReport from "./components/EvaluationReport";
import ProfileScreen from "./components/ProfileScreen";
import LeaderboardScreen from "./components/LeaderboardScreen";

/**
 * AppContent — Ana uygulama içeriği (auth gerekli)
 * Login → Başlangıç → Simülasyon → Değerlendirme
 * + Profil & Liderlik Tablosu
 */
function AppContent() {
  const { user, loading, logout } = useAuth();

  // ── Ekran yönetimi ────────────────────────────────────
  const [screen, setScreen] = useState("start");
  const [scenario, setScenario] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [actions, setActions] = useState([]);
  const [evaluation, setEvaluation] = useState(null);
  const [sessionResult, setSessionResult] = useState(null);

  // Yüklenirken bekle
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  // Giriş yapılmamışsa login ekranı
  if (!user) {
    return <LoginScreen />;
  }

  const handleScenarioReady = (newScenario, newSessionId, difficulty) => {
    setScenario(newScenario);
    setSessionId(newSessionId);
    setChatHistory([]);
    setActions([]);
    setEvaluation(null);
    setSessionResult(null);
    setScreen("simulation");
  };

  const handleEvaluationReady = (evalData, sessResult) => {
    setEvaluation(evalData);
    setSessionResult(sessResult || null);
    setScreen("evaluation");
  };

  const handleRestart = () => {
    setScenario(null);
    setSessionId(null);
    setChatHistory([]);
    setActions([]);
    setEvaluation(null);
    setSessionResult(null);
    setScreen("start");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-emerald-50/20">
      {/* Üst Nav Bar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100 px-3 sm:px-4 py-2 flex items-center justify-between gap-2">
        <div
          className="flex items-center gap-1.5 sm:gap-2 cursor-pointer flex-shrink-0"
          onClick={handleRestart}
        >
          <span className="text-lg sm:text-xl">🏥</span>
          <span className="font-bold text-gray-800 text-sm sm:text-base">AntrenmanAI</span>
        </div>
        <div className="flex items-center gap-1.5 sm:gap-2">
          {/* Profil butonu */}
          <button
            onClick={() => setScreen("profile")}
            className={`text-xs px-2 sm:px-3 py-1.5 rounded-lg transition-colors ${
              screen === "profile"
                ? "bg-indigo-100 text-indigo-700"
                : "bg-gray-50 hover:bg-gray-100 text-gray-600"
            }`}
          >
            👤 <span className="hidden sm:inline">Profil</span>
          </button>
          {/* Liderlik butonu */}
          <button
            onClick={() => setScreen("leaderboard")}
            className={`text-xs px-2 sm:px-3 py-1.5 rounded-lg transition-colors ${
              screen === "leaderboard"
                ? "bg-amber-100 text-amber-700"
                : "bg-gray-50 hover:bg-gray-100 text-gray-600"
            }`}
          >
            🏆 <span className="hidden sm:inline">Sıralama</span>
          </button>
          <div className="w-px h-5 bg-gray-200 mx-0.5 sm:mx-1 hidden sm:block" />
          {user.picture && (
            <img
              src={user.picture}
              alt={user.name}
              className="w-7 h-7 sm:w-8 sm:h-8 rounded-full border-2 border-gray-200"
            />
          )}
          <span className="text-sm text-gray-600 hidden md:block">
            {user.name || user.email}
          </span>
          <button
            onClick={logout}
            className="text-xs px-2 sm:px-3 py-1.5 rounded-lg bg-gray-100 hover:bg-gray-200 
                       text-gray-600 transition-colors"
          >
            <span className="hidden sm:inline">Çıkış</span>
            <span className="sm:hidden">✕</span>
          </button>
        </div>
      </nav>

      {/* Ana İçerik (navbar yüksekliği kadar padding) */}
      <div className="pt-14">
        {screen === "start" && (
          <StartScreen onScenarioReady={handleScenarioReady} />
        )}

        {screen === "simulation" && scenario && (
          <SimulationScreen
            scenario={scenario}
            sessionId={sessionId}
            chatHistory={chatHistory}
            setChatHistory={setChatHistory}
            actions={actions}
            setActions={setActions}
            onEvaluationReady={handleEvaluationReady}
            onRestart={handleRestart}
          />
        )}

        {screen === "evaluation" && evaluation && (
          <EvaluationReport
            evaluation={evaluation}
            scenario={scenario}
            sessionResult={sessionResult}
            onRestart={handleRestart}
          />
        )}

        {screen === "profile" && (
          <ProfileScreen onBack={handleRestart} />
        )}

        {screen === "leaderboard" && (
          <LeaderboardScreen onBack={handleRestart} />
        )}
      </div>
    </div>
  );
}

/**
 * App — AuthProvider ile sarılmış kök bileşen
 */
export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
