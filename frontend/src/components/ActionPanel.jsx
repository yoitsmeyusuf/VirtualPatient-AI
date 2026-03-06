import { useState } from "react";
import {
  Stethoscope,
  TestTubes,
  Loader2,
  CheckCircle2,
  ChevronRight,
} from "lucide-react";
import * as api from "../api";

const EXAM_AREAS = [
  { key: "vital_signs", label: "Vital Bulgular", icon: "💓" },
  { key: "general", label: "Genel Görünüm", icon: "👁️" },
  { key: "abdomen", label: "Karın Muayenesi", icon: "🩺" },
  { key: "chest", label: "Göğüs Muayenesi", icon: "🫁" },
];

const TEST_TYPES = [
  { key: "complete_blood_count", label: "Hemogram", icon: "🩸" },
  { key: "biochemistry", label: "Biyokimya", icon: "🧪" },
  { key: "urinalysis", label: "İdrar Tahlili", icon: "🧫" },
  { key: "xray", label: "Röntgen", icon: "📷" },
  { key: "ultrasound", label: "Ultrason", icon: "📡" },
  { key: "ct_scan", label: "BT Tarama", icon: "🖥️" },
];

export default function ActionPanel({ scenario, actions, setActions }) {
  const [tab, setTab] = useState("exam"); // exam | test
  const [loading, setLoading] = useState(null); // hangi buton yükleniyor
  const [results, setResults] = useState({}); // key → result

  const handleExam = async (area) => {
    setLoading(area.key);
    try {
      const data = await api.examine(area.key, scenario);
      const resultText = data.findings;
      setResults((prev) => ({ ...prev, [area.key]: resultText }));
      setActions((prev) => [
        ...prev,
        `Muayene: ${data.area} → ${resultText}`,
      ]);
    } catch (err) {
      setResults((prev) => ({
        ...prev,
        [area.key]: "⚠️ Hata: " + err.message,
      }));
    } finally {
      setLoading(null);
    }
  };

  const handleTest = async (test) => {
    setLoading(test.key);
    try {
      const data = await api.orderTest(test.key, scenario);
      const resultText =
        typeof data.results === "object"
          ? Object.entries(data.results)
              .map(([k, v]) => `${k}: ${v}`)
              .join("\n")
          : data.results;
      setResults((prev) => ({ ...prev, [test.key]: resultText }));
      setActions((prev) => [...prev, `Tetkik: ${data.test_name}`]);
    } catch (err) {
      setResults((prev) => ({
        ...prev,
        [test.key]: "⚠️ Hata: " + err.message,
      }));
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="card flex flex-col h-full">
      {/* Tab başlıkları */}
      <div className="flex border-b border-gray-100">
        <TabButton
          active={tab === "exam"}
          onClick={() => setTab("exam")}
          icon={<Stethoscope className="w-4 h-4" />}
          label="Muayene"
        />
        <TabButton
          active={tab === "test"}
          onClick={() => setTab("test")}
          icon={<TestTubes className="w-4 h-4" />}
          label="Tetkik"
        />
      </div>

      {/* İçerik */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {tab === "exam" &&
          EXAM_AREAS.map((area) => (
            <ActionItem
              key={area.key}
              item={area}
              result={results[area.key]}
              loading={loading === area.key}
              onAction={() => handleExam(area)}
            />
          ))}

        {tab === "test" &&
          TEST_TYPES.map((test) => (
            <ActionItem
              key={test.key}
              item={test}
              result={results[test.key]}
              loading={loading === test.key}
              onAction={() => handleTest(test)}
            />
          ))}
      </div>
    </div>
  );
}

function TabButton({ active, onClick, icon, label }) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 flex items-center justify-center gap-1.5 py-3 text-sm font-medium
                  transition-all border-b-2 ${
                    active
                      ? "border-primary-500 text-primary-600"
                      : "border-transparent text-gray-400 hover:text-gray-600"
                  }`}
    >
      {icon} {label}
    </button>
  );
}

function ActionItem({ item, result, loading, onAction }) {
  const done = !!result;

  return (
    <div className="rounded-xl border border-gray-100 overflow-hidden">
      <button
        onClick={onAction}
        disabled={loading || done}
        className={`w-full flex items-center gap-3 px-3.5 py-3 text-left 
                    transition-all text-sm ${
                      done
                        ? "bg-medical-50/50"
                        : "hover:bg-gray-50 active:bg-gray-100"
                    } disabled:cursor-default`}
      >
        <span className="text-lg">{item.icon}</span>
        <span
          className={`flex-1 font-medium ${
            done ? "text-medical-700" : "text-gray-700"
          }`}
        >
          {item.label}
        </span>
        {loading && <Loader2 className="w-4 h-4 animate-spin text-gray-400" />}
        {done && <CheckCircle2 className="w-4 h-4 text-medical-500" />}
        {!loading && !done && (
          <ChevronRight className="w-4 h-4 text-gray-300" />
        )}
      </button>

      {done && (
        <div className="px-3.5 pb-3 text-xs text-gray-600 whitespace-pre-line border-t border-gray-50 pt-2">
          {result}
        </div>
      )}
    </div>
  );
}
