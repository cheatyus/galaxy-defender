import os
import sqlite3
from src.infrastructure.utils import resource_path


class DatabaseManager:

    def __init__(self, db_filename: str = "data/savegame.db"):
        self.db_path = resource_path(db_filename)
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def init_database(self) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS player_save ("
            "id INTEGER PRIMARY KEY, "
            "current_level INTEGER DEFAULT 1, "
            "credits INTEGER DEFAULT 0, "
            "score INTEGER DEFAULT 0, "
            "enemies_killed INTEGER DEFAULT 0, "
            "damage_level INTEGER DEFAULT 1, "
            "health_level INTEGER DEFAULT 1, "
            "firerate_level INTEGER DEFAULT 1, "
            "speed_level INTEGER DEFAULT 1, "
            "double_cannon INTEGER DEFAULT 0, "
            "shield_level INTEGER DEFAULT 0, "
            "triple_cannon INTEGER DEFAULT 0, "
            "magnet_level INTEGER DEFAULT 0)"
        )

        cursor.execute("PRAGMA table_info(player_save)")
        existing_cols = [col[1] for col in cursor.fetchall()]

        if "shield_level" not in existing_cols:
            cursor.execute("ALTER TABLE player_save ADD COLUMN shield_level INTEGER DEFAULT 0")
        if "triple_cannon" not in existing_cols:
            cursor.execute("ALTER TABLE player_save ADD COLUMN triple_cannon INTEGER DEFAULT 0")
        if "magnet_level" not in existing_cols:
            cursor.execute("ALTER TABLE player_save ADD COLUMN magnet_level INTEGER DEFAULT 0")

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS high_scores ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "player_name TEXT DEFAULT 'Piloto', "
            "score INTEGER NOT NULL, "
            "level_reached INTEGER NOT NULL, "
            "date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        )

        cursor.execute("SELECT COUNT(*) FROM player_save WHERE id = 1")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO player_save ("
                "id, current_level, credits, score, enemies_killed, "
                "damage_level, health_level, firerate_level, speed_level, "
                "double_cannon, shield_level, triple_cannon, magnet_level"
                ") VALUES (1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0)"
            )

        conn.commit()
        conn.close()

    def load_save(self) -> dict:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT current_level, credits, score, enemies_killed, "
            "damage_level, health_level, firerate_level, speed_level, "
            "double_cannon, shield_level, triple_cannon, magnet_level "
            "FROM player_save WHERE id = 1"
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "current_level": row[0],
                "credits": row[1],
                "score": row[2],
                "enemies_killed": row[3],
                "damage_level": row[4],
                "health_level": row[5],
                "firerate_level": row[6],
                "speed_level": row[7],
                "double_cannon": bool(row[8]),
                "shield_level": row[9] if len(row) > 9 and row[9] is not None else 0,
                "triple_cannon": bool(row[10]) if len(row) > 10 and row[10] is not None else False,
                "magnet_level": row[11] if len(row) > 11 and row[11] is not None else 0,
            }

        return {
            "current_level": 1,
            "credits": 0,
            "score": 0,
            "enemies_killed": 0,
            "damage_level": 1,
            "health_level": 1,
            "firerate_level": 1,
            "speed_level": 1,
            "double_cannon": False,
            "shield_level": 0,
            "triple_cannon": False,
            "magnet_level": 0,
        }

    def save_game(
        self,
        current_level: int,
        credits: int,
        score: int,
        enemies_killed: int,
        damage_level: int,
        health_level: int,
        firerate_level: int,
        speed_level: int,
        double_cannon: bool,
        shield_level: int = 0,
        triple_cannon: bool = False,
        magnet_level: int = 0,
    ) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE player_save SET "
            "current_level = ?, "
            "credits = ?, "
            "score = ?, "
            "enemies_killed = ?, "
            "damage_level = ?, "
            "health_level = ?, "
            "firerate_level = ?, "
            "speed_level = ?, "
            "double_cannon = ?, "
            "shield_level = ?, "
            "triple_cannon = ?, "
            "magnet_level = ? "
            "WHERE id = 1",
            (
                current_level,
                credits,
                score,
                enemies_killed,
                damage_level,
                health_level,
                firerate_level,
                speed_level,
                1 if double_cannon else 0,
                shield_level,
                1 if triple_cannon else 0,
                magnet_level,
            ),
        )
        conn.commit()
        conn.close()

    def record_score(self, score: int, level: int, player_name: str = "Piloto") -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO high_scores (player_name, score, level_reached) VALUES (?, ?, ?)",
            (player_name, score, level),
        )
        conn.commit()
        conn.close()

    def reset_save(self) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE player_save SET "
            "current_level = 1, "
            "credits = 0, "
            "score = 0, "
            "enemies_killed = 0, "
            "damage_level = 1, "
            "health_level = 1, "
            "firerate_level = 1, "
            "speed_level = 1, "
            "double_cannon = 0, "
            "shield_level = 0, "
            "triple_cannon = 0, "
            "magnet_level = 0 "
            "WHERE id = 1"
        )
        conn.commit()
        conn.close()
