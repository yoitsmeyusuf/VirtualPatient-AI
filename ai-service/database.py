"""
database.py — SQLite Veritabanı Katmanı (aiosqlite)
-------------------------------------------------------
Tablolar:
  users       — Kullanıcı profili + ELO rating
  sessions    — Simülasyon oturumları
  chat_logs   — Mesaj geçmişi
  achievements— Kazanılan rozetler
"""

import json
import time
from pathlib import Path

import aiosqlite

# Render disk mount: /data varsa orayı kullan, yoksa yerel dizin
_data_dir = Path("/data") if Path("/data").exists() and Path("/data").is_dir() else Path(__file__).parent
DB_PATH = _data_dir / "antrenman.db"

# ── ELO Sabitleri ────────────────────────────────────────────────────
ELO_START = 1000
ELO_K = 32  # K-faktörü


# ═══════════════════════════════════════════════════════════════════════
# TABLO OLUŞTURMA
# ═══════════════════════════════════════════════════════════════════════

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          TEXT PRIMARY KEY,           -- Google sub veya dev-user-001
    email       TEXT NOT NULL DEFAULT '',
    name        TEXT NOT NULL DEFAULT '',
    picture     TEXT NOT NULL DEFAULT '',
    elo_rating  INTEGER NOT NULL DEFAULT 1000,
    total_sessions  INTEGER NOT NULL DEFAULT 0,
    correct_diagnoses INTEGER NOT NULL DEFAULT 0,
    xp          INTEGER NOT NULL DEFAULT 0,
    level       INTEGER NOT NULL DEFAULT 1,
    streak_days INTEGER NOT NULL DEFAULT 0,
    last_played TEXT NOT NULL DEFAULT '',   -- YYYY-MM-DD
    created_at  REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         TEXT NOT NULL REFERENCES users(id),
    topic           TEXT NOT NULL DEFAULT '',
    difficulty      TEXT NOT NULL DEFAULT 'Orta',
    scenario_json   TEXT NOT NULL DEFAULT '{}',
    chat_history    TEXT NOT NULL DEFAULT '[]',
    actions_taken   TEXT NOT NULL DEFAULT '[]',
    student_diagnosis TEXT,
    correct_diagnosis TEXT,
    diagnosis_correct INTEGER DEFAULT 0,
    evaluation_json TEXT,
    treatment_json  TEXT,
    overall_score   INTEGER DEFAULT 0,
    elo_change      INTEGER DEFAULT 0,
    xp_earned       INTEGER DEFAULT 0,
    emotion_log     TEXT NOT NULL DEFAULT '[]',
    started_at      REAL NOT NULL DEFAULT 0,
    completed_at    REAL
);

CREATE TABLE IF NOT EXISTS achievements (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL REFERENCES users(id),
    badge_id    TEXT NOT NULL,
    badge_name  TEXT NOT NULL,
    badge_icon  TEXT NOT NULL DEFAULT '🏆',
    earned_at   REAL NOT NULL DEFAULT 0,
    UNIQUE(user_id, badge_id)
);
"""


async def init_db():
    """Veritabanını oluşturur (yoksa), tabloları kurar."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_SCHEMA)
        await db.commit()


# ═══════════════════════════════════════════════════════════════════════
# USER İŞLEMLERİ
# ═══════════════════════════════════════════════════════════════════════

async def upsert_user(user_data: dict) -> dict:
    """
    Kullanıcıyı oluşturur veya günceller. Profil bilgisini döner.
    """
    uid = user_data["sub"]
    now = time.time()

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Var mı kontrol
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (uid,))
        row = await cursor.fetchone()

        if row is None:
            await db.execute(
                """INSERT INTO users (id, email, name, picture, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (uid, user_data.get("email", ""),
                 user_data.get("name", ""),
                 user_data.get("picture", ""), now),
            )
            await db.commit()
            cursor = await db.execute("SELECT * FROM users WHERE id = ?", (uid,))
            row = await cursor.fetchone()
        else:
            # İsim/resim güncelle
            await db.execute(
                "UPDATE users SET name=?, picture=? WHERE id=?",
                (user_data.get("name", ""), user_data.get("picture", ""), uid),
            )
            await db.commit()

        return dict(row)


async def get_user(user_id: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_leaderboard(limit: int = 20) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT id, name, picture, elo_rating, level, xp,
                      total_sessions, correct_diagnoses
               FROM users ORDER BY elo_rating DESC LIMIT ?""",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════════════
# SESSION İŞLEMLERİ
# ═══════════════════════════════════════════════════════════════════════

async def create_session(
    user_id: str,
    topic: str,
    difficulty: str,
    scenario: dict,
) -> int:
    """Yeni oturum oluşturur, session ID döner."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO sessions
               (user_id, topic, difficulty, scenario_json,
                correct_diagnosis, started_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, topic, difficulty,
             json.dumps(scenario, ensure_ascii=False),
             scenario.get("correct_diagnosis", ""),
             time.time()),
        )
        await db.commit()
        return cursor.lastrowid


async def update_session_chat(session_id: int, chat_history: list, actions: list):
    """Sohbet geçmişini ve aksiyonları günceller."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """UPDATE sessions SET chat_history=?, actions_taken=? WHERE id=?""",
            (json.dumps(chat_history, ensure_ascii=False),
             json.dumps(actions, ensure_ascii=False),
             session_id),
        )
        await db.commit()


async def complete_session(
    session_id: int,
    user_id: str,
    evaluation: dict,
    student_diagnosis: str | None,
    treatment: dict | None,
    emotion_log: list | None,
) -> dict:
    """
    Oturumu tamamlar: skoru kaydeder, ELO + XP hesaplar, rozet kontrol eder.
    Güncel kullanıcı profilini döner.
    """
    overall_score = evaluation.get("overall_score", 5)
    diag_correct = evaluation.get("diagnosis_correct", False)

    # ── XP Hesaplama ─────────────────────────────────────────────────
    xp_earned = overall_score * 10  # base
    if diag_correct:
        xp_earned += 50  # bonus

    # ── ELO Hesaplama ────────────────────────────────────────────────
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = dict(await cursor.fetchone())

        cursor2 = await db.execute("SELECT difficulty FROM sessions WHERE id = ?", (session_id,))
        sess_row = await cursor2.fetchone()
        difficulty = dict(sess_row).get("difficulty", "Orta") if sess_row else "Orta"

        expected_score_map = {"Kolay": 0.75, "Orta": 0.5, "Zor": 0.25}
        expected = expected_score_map.get(difficulty, 0.5)
        actual = min(overall_score / 10, 1.0)
        elo_change = round(ELO_K * (actual - expected))
        new_elo = max(100, user["elo_rating"] + elo_change)

        # ── Streak ───────────────────────────────────────────────────
        from datetime import date
        today = date.today().isoformat()
        if user["last_played"] == today:
            new_streak = user["streak_days"]
        elif user["last_played"] == str(date.today().replace(
            day=date.today().day - 1
        )) if date.today().day > 1 else "":
            new_streak = user["streak_days"] + 1
        else:
            new_streak = 1

        # ── Level ────────────────────────────────────────────────────
        new_xp = user["xp"] + xp_earned
        new_level = 1 + new_xp // 500  # Her 500 XP = 1 seviye

        # ── Kullanıcı güncelle ───────────────────────────────────────
        await db.execute(
            """UPDATE users SET
                 elo_rating = ?,
                 total_sessions = total_sessions + 1,
                 correct_diagnoses = correct_diagnoses + ?,
                 xp = ?,
                 level = ?,
                 streak_days = ?,
                 last_played = ?
               WHERE id = ?""",
            (new_elo,
             1 if diag_correct else 0,
             new_xp, new_level, new_streak, today, user_id),
        )

        # ── Oturumu tamamla ──────────────────────────────────────────
        await db.execute(
            """UPDATE sessions SET
                 evaluation_json = ?,
                 treatment_json = ?,
                 student_diagnosis = ?,
                 diagnosis_correct = ?,
                 overall_score = ?,
                 elo_change = ?,
                 xp_earned = ?,
                 emotion_log = ?,
                 completed_at = ?
               WHERE id = ?""",
            (json.dumps(evaluation, ensure_ascii=False),
             json.dumps(treatment, ensure_ascii=False) if treatment else None,
             student_diagnosis,
             1 if diag_correct else 0,
             overall_score, elo_change, xp_earned,
             json.dumps(emotion_log or [], ensure_ascii=False),
             time.time(), session_id),
        )

        await db.commit()

        # ── Rozet Kontrolü ───────────────────────────────────────────
        new_total = user["total_sessions"] + 1
        new_correct = user["correct_diagnoses"] + (1 if diag_correct else 0)

        badges_to_check = [
            ("first_session", "İlk Adım", "👶", new_total >= 1),
            ("five_sessions", "Deneyimli", "🎓", new_total >= 5),
            ("ten_sessions", "Veteran", "🏅", new_total >= 10),
            ("fifty_sessions", "Uzman", "👨‍⚕️", new_total >= 50),
            ("first_correct", "İlk Doğru Tanı", "🎯", new_correct >= 1),
            ("ten_correct", "Keskin Göz", "🔬", new_correct >= 10),
            ("perfect_score", "Mükemmel Skor", "⭐", overall_score == 10),
            ("streak_3", "3 Gün Serisi", "🔥", new_streak >= 3),
            ("streak_7", "Haftalık Seri", "💪", new_streak >= 7),
            ("streak_30", "Ay Serisi", "🏆", new_streak >= 30),
            ("elo_1200", "Bronz Doktor", "🥉", new_elo >= 1200),
            ("elo_1500", "Gümüş Doktor", "🥈", new_elo >= 1500),
            ("elo_1800", "Altın Doktor", "🥇", new_elo >= 1800),
            ("elo_2000", "Efsane Doktor", "💎", new_elo >= 2000),
            ("level_5", "Seviye 5", "📈", new_level >= 5),
            ("level_10", "Seviye 10", "🚀", new_level >= 10),
        ]

        new_badges = []
        for badge_id, badge_name, icon, condition in badges_to_check:
            if condition:
                try:
                    await db.execute(
                        """INSERT OR IGNORE INTO achievements
                           (user_id, badge_id, badge_name, badge_icon, earned_at)
                           VALUES (?, ?, ?, ?, ?)""",
                        (user_id, badge_id, badge_name, icon, time.time()),
                    )
                    # Gerçekten yeni eklendiyse
                    if db.total_changes > 0:
                        new_badges.append({"id": badge_id, "name": badge_name, "icon": icon})
                except Exception:
                    pass

        await db.commit()

    updated_user = await get_user(user_id)
    return {
        "user": updated_user,
        "session_result": {
            "overall_score": overall_score,
            "diagnosis_correct": diag_correct,
            "elo_change": elo_change,
            "elo_after": new_elo,
            "xp_earned": xp_earned,
            "new_level": new_level,
            "new_badges": new_badges,
        },
    }


async def get_user_sessions(user_id: str, limit: int = 20) -> list[dict]:
    """Kullanıcının son oturumlarını döner."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT id, topic, difficulty, correct_diagnosis,
                      student_diagnosis, diagnosis_correct,
                      overall_score, elo_change, xp_earned,
                      started_at, completed_at
               FROM sessions WHERE user_id = ? AND completed_at IS NOT NULL
               ORDER BY completed_at DESC LIMIT ?""",
            (user_id, limit),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_user_achievements(user_id: str) -> list[dict]:
    """Kullanıcının tüm rozetlerini döner."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM achievements WHERE user_id = ? ORDER BY earned_at DESC",
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_user_stats(user_id: str) -> dict:
    """Kullanıcının detaylı istatistiklerini döner."""
    user = await get_user(user_id)
    if not user:
        return {}

    sessions = await get_user_sessions(user_id, limit=100)
    achievements = await get_user_achievements(user_id)

    # Zorluk dağılımı
    diff_counts = {"Kolay": 0, "Orta": 0, "Zor": 0}
    score_sum = 0
    for s in sessions:
        diff_counts[s.get("difficulty", "Orta")] = diff_counts.get(s.get("difficulty", "Orta"), 0) + 1
        score_sum += s.get("overall_score", 0)

    avg_score = round(score_sum / len(sessions), 1) if sessions else 0
    accuracy = round(user["correct_diagnoses"] / user["total_sessions"] * 100, 1) if user["total_sessions"] > 0 else 0

    return {
        "user": user,
        "total_sessions": user["total_sessions"],
        "correct_diagnoses": user["correct_diagnoses"],
        "accuracy_percent": accuracy,
        "average_score": avg_score,
        "elo_rating": user["elo_rating"],
        "level": user["level"],
        "xp": user["xp"],
        "xp_to_next_level": 500 - (user["xp"] % 500),
        "streak_days": user["streak_days"],
        "difficulty_distribution": diff_counts,
        "recent_sessions": sessions[:10],
        "achievements": achievements,
    }
