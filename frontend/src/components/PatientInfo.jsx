import { useState } from "react";
import {
  User,
  Heart,
  Pill,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Briefcase,
  Clock,
} from "lucide-react";

export default function PatientInfo({ scenario }) {
  const [expanded, setExpanded] = useState(false);

  if (!scenario) return null;

  const vs = scenario.vital_signs || {};

  return (
    <div className="card overflow-hidden">
      {/* Hasta başlığı */}
      <div className="p-4 bg-gradient-to-r from-primary-600 to-primary-700 text-white">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
            <User className="w-6 h-6" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-lg truncate">
              {scenario.patient_name}
            </h3>
            <p className="text-primary-100 text-sm">
              {scenario.age} yaş • {scenario.gender}
            </p>
          </div>
          <span
            className={`badge text-xs ${
              scenario.difficulty_level === "Kolay"
                ? "bg-green-400/20 text-green-100"
                : scenario.difficulty_level === "Zor"
                ? "bg-red-400/20 text-red-100"
                : "bg-yellow-400/20 text-yellow-100"
            }`}
          >
            {scenario.difficulty_level}
          </span>
        </div>
      </div>

      {/* Ana şikayet */}
      <div className="p-4 border-b border-gray-100">
        <p className="text-sm text-gray-500 mb-1">Ana Şikayet</p>
        <p className="text-sm font-medium text-gray-800">
          "{scenario.chief_complaint}"
        </p>
      </div>

      {/* Vitaller — her zaman görünür */}
      <div className="p-4 border-b border-gray-100">
        <p className="text-sm text-gray-500 mb-2 flex items-center gap-1.5">
          <Heart className="w-3.5 h-3.5" /> Vital Bulgular
        </p>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <Vital label="TA" value={vs.blood_pressure} />
          <Vital label="Nabız" value={vs.heart_rate} />
          <Vital label="Ateş" value={vs.temperature} />
          <Vital label="SpO₂" value={vs.spo2} />
        </div>
      </div>

      {/* Genişletme düğmesi */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-2.5 text-sm text-gray-500 hover:bg-gray-50 
                   flex items-center justify-center gap-1 transition-colors"
      >
        {expanded ? (
          <>
            <ChevronUp className="w-4 h-4" /> Daralt
          </>
        ) : (
          <>
            <ChevronDown className="w-4 h-4" /> Detaylar
          </>
        )}
      </button>

      {/* Genişletilmiş detaylar */}
      {expanded && (
        <div className="border-t border-gray-100 divide-y divide-gray-50">
          <InfoRow
            icon={<Briefcase className="w-3.5 h-3.5" />}
            label="Meslek"
            value={scenario.occupation}
          />
          <InfoRow
            icon={<Clock className="w-3.5 h-3.5" />}
            label="Geçmiş"
            value={
              scenario.past_medical_history?.join(", ") || "Yok"
            }
          />
          <InfoRow
            icon={<Pill className="w-3.5 h-3.5" />}
            label="İlaçlar"
            value={scenario.medications?.join(", ") || "Yok"}
          />
          <InfoRow
            icon={<AlertTriangle className="w-3.5 h-3.5" />}
            label="Alerjiler"
            value={scenario.allergies?.join(", ") || "Yok"}
          />
        </div>
      )}
    </div>
  );
}

function Vital({ label, value }) {
  return (
    <div className="bg-gray-50 rounded-lg px-2.5 py-1.5">
      <span className="text-gray-400">{label}: </span>
      <span className="font-medium text-gray-700">{value || "—"}</span>
    </div>
  );
}

function InfoRow({ icon, label, value }) {
  return (
    <div className="px-4 py-3 flex items-start gap-2">
      <span className="text-gray-400 mt-0.5">{icon}</span>
      <div>
        <p className="text-xs text-gray-400">{label}</p>
        <p className="text-sm text-gray-700">{value}</p>
      </div>
    </div>
  );
}
