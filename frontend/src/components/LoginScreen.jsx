/**
 * LoginScreen.jsx — Google ile Giriş Ekranı
 */
import { useState, useEffect, useRef } from "react";
import { useAuth } from "../context/AuthContext";
import { LogIn, Stethoscope, AlertCircle } from "lucide-react";

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

export default function LoginScreen() {
  const { login } = useAuth();
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const googleBtnRef = useRef(null);

  useEffect(() => {
    // Google Identity Services yükle
    if (!GOOGLE_CLIENT_ID || GOOGLE_CLIENT_ID === "YOUR_GOOGLE_CLIENT_ID_HERE") {
      return; // Google Client ID ayarlanmamış
    }

    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.onload = () => {
      if (window.google) {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleGoogleResponse,
        });
        if (googleBtnRef.current) {
          window.google.accounts.id.renderButton(googleBtnRef.current, {
            theme: "outline",
            size: "large",
            text: "signin_with",
            locale: "tr",
            width: 300,
          });
        }
      }
    };
    document.head.appendChild(script);

    return () => {
      document.head.removeChild(script);
    };
  }, []);

  const handleGoogleResponse = async (response) => {
    setError(null);
    setLoading(true);
    try {
      await login(response.credential);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Google Client ID yoksa dev mode'da geçiş butonu göster
  const handleDevLogin = async () => {
    setError(null);
    setLoading(true);
    try {
      // Dev modda JWT almak için basit bir bypass
      const res = await fetch("/api/auth/google", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ credential: "dev-mode-token" }),
      });
      if (!res.ok) throw new Error("Backend bağlantısı başarısız");
      const data = await res.json();
      // Login fonksiyonunu doğrudan set et
      localStorage.setItem("antrenman_jwt", data.token);
      localStorage.setItem("antrenman_user", JSON.stringify(data.user));
      window.location.reload();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-blue-50/30 to-emerald-50/20">
      <div className="w-full max-w-md">
        {/* Logo / Başlık */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-emerald-500 text-white mb-4 shadow-lg">
            <Stethoscope className="w-10 h-10" />
          </div>
          <h1 className="text-3xl font-bold text-gray-800">AntrenmanAI</h1>
          <p className="text-gray-500 mt-2">
            Tıp Eğitim Simülatörü
          </p>
        </div>

        {/* Kart */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          <h2 className="text-xl font-semibold text-center text-gray-800 mb-2">
            Hoş Geldiniz
          </h2>
          <p className="text-sm text-gray-500 text-center mb-6">
            Devam etmek için Google hesabınızla giriş yapın
          </p>

          {/* Hata mesajı */}
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Google Giriş Butonu */}
          <div className="flex flex-col items-center gap-4">
            {GOOGLE_CLIENT_ID && GOOGLE_CLIENT_ID !== "YOUR_GOOGLE_CLIENT_ID_HERE" ? (
              <div ref={googleBtnRef} className="flex justify-center" />
            ) : (
              <>
                <p className="text-xs text-amber-600 bg-amber-50 p-3 rounded-lg border border-amber-200 text-center">
                  ⚠️ Google Client ID henüz ayarlanmamış.
                  <br />
                  <code className="text-[10px]">frontend/.env</code> dosyasına ekleyin.
                </p>
                <button
                  onClick={handleDevLogin}
                  disabled={loading}
                  className="flex items-center gap-2 px-6 py-3 bg-gray-800 text-white rounded-xl
                           hover:bg-gray-700 transition-colors text-sm font-medium shadow-md"
                >
                  <LogIn className="w-4 h-4" />
                  {loading ? "Giriş yapılıyor..." : "Geliştirici Girişi (Dev)"}
                </button>
              </>
            )}
          </div>

          {/* Bilgi */}
          <div className="mt-8 pt-6 border-t border-gray-100">
            <div className="grid grid-cols-3 gap-3 text-center">
              <div>
                <div className="text-2xl mb-1">🤖</div>
                <p className="text-[11px] text-gray-500">AI Hasta</p>
              </div>
              <div>
                <div className="text-2xl mb-1">🩺</div>
                <p className="text-[11px] text-gray-500">Muayene</p>
              </div>
              <div>
                <div className="text-2xl mb-1">📊</div>
                <p className="text-[11px] text-gray-500">Değerlendirme</p>
              </div>
            </div>
          </div>
        </div>

        <p className="text-center text-xs text-gray-400 mt-6">
          GPT-4o-mini ile güçlendirilmiştir 🚀
        </p>
      </div>
    </div>
  );
}
