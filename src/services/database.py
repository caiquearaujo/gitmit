"""Service for the SQLite database."""

import sqlite3

from pathlib import Path
from datetime import datetime, timedelta


class LLMUsageDatabaseService:
    """Service for the management of LLM usage on a SQLite database."""

    def __init__(self):
        """Initialize the SQLiteService class.

        Args:
            file (str): The file to be used.
        """
        path = Path.home() / ".config" / "gitmit"
        path.mkdir(parents=True, exist_ok=True)

        self.file = path.joinpath("llm_usage.db").as_posix()
        self.conn = sqlite3.connect(self.file)
        self.cursor = self.conn.cursor()
        self.__create_table()

    def __create_table(self):
        """Create the table if it doesn't exist."""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tokens_counter (
                timestamp TEXT,
                year INTEGER,
                month INTEGER,
                tokens_used INTEGER
            )
        """
        )

        self.conn.commit()

    def insert_token_usage(self, tokens_used: int):
        """Insert the token usage into the table.

        Args:
            tokens_used (int): The number of tokens used.
        """
        timestamp = datetime.now()

        year = timestamp.year
        month = timestamp.month
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute(
            "INSERT INTO tokens_counter (timestamp, year, month, tokens_used) VALUES (?, ?, ?, ?)",
            (timestamp_str, year, month, tokens_used),
        )

        self.conn.commit()

    def current_month_tokens_used(self):
        """Get the current month tokens used.

        Returns:
            int: The number of tokens used.
        """
        self.cursor.execute(
            "SELECT SUM(tokens_used) FROM tokens_counter WHERE year = ? AND month = ?",
            (datetime.now().year, datetime.now().month),
        )

        token_sum = self.cursor.fetchone()[0]
        return token_sum if token_sum is not None else 0

    def flush_old_tokens(self):
        """Flush old tokens usage before last 30 days."""
        self.cursor.execute(
            "DELETE FROM tokens_counter WHERE timestamp < ?",
            (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
        )

        self.conn.commit()

    def close(self):
        """Close the connection to the database."""
        self.conn.close()
