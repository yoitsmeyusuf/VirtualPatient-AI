import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Bot, UserRound } from "lucide-react";

export default function ChatPanel({
  scenario,
  chatHistory,
  setChatHistory,
  onSend,
}) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  // Otomatik scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  const handleSend = async () => {
    const text = message.trim();
    if (!text || loading) return;

    setMessage("");
    setLoading(true);

    try {
      if (onSend) {
        // Parent (SimulationScreen) handles API call with emotion + session
        await onSend(text);
      }
    } catch (err) {
      // Hata parent'ta handle ediliyor
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="card flex flex-col h-full">
      {/* Başlık */}
      <div className="px-5 py-3.5 border-b border-gray-100 flex items-center gap-2">
        <Bot className="w-5 h-5 text-medical-600" />
        <h2 className="font-semibold text-gray-800">Hasta Görüşmesi</h2>
        <span className="ml-auto text-xs text-gray-400">
          {chatHistory.length} mesaj
        </span>
      </div>

      {/* Mesaj alanı */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
        {chatHistory.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-gray-400 text-sm">
            <Bot className="w-12 h-12 mb-3 text-gray-300" />
            <p>Hastaya soru sormaya başlayın</p>
            <p className="text-xs mt-1">Örn: "Merhaba, bugün nasıl hissediyorsunuz?"</p>
          </div>
        )}

        {chatHistory.map((msg, i) => (
          <ChatBubble key={i} msg={msg} />
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-gray-400 text-sm pl-12">
            <Loader2 className="w-4 h-4 animate-spin" />
            Hasta düşünüyor...
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Giriş alanı */}
      <div className="p-4 border-t border-gray-100">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Hastaya sorunuzu yazın..."
            className="flex-1 px-4 py-3 rounded-xl border border-gray-200 
                       focus:border-primary-400 focus:ring-2 focus:ring-primary-100 
                       outline-none transition-all text-sm"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !message.trim()}
            className="btn-primary !p-3 !rounded-xl"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

function ChatBubble({ msg }) {
  const isDoctor = msg.role === "doctor";

  return (
    <div className={`flex gap-2.5 ${isDoctor ? "flex-row-reverse" : ""}`}>
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isDoctor
            ? "bg-primary-100 text-primary-600"
            : "bg-medical-100 text-medical-600"
        }`}
      >
        {isDoctor ? (
          <UserRound className="w-4 h-4" />
        ) : (
          <Bot className="w-4 h-4" />
        )}
      </div>
      <div
        className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
          isDoctor
            ? "bg-primary-600 text-white rounded-tr-md"
            : "bg-gray-100 text-gray-800 rounded-tl-md"
        }`}
      >
        {msg.content}
      </div>
    </div>
  );
}
