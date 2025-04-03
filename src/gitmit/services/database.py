"""Service for the SQLite database."""

import mysql.connector
import sys

from pydantic import BaseModel
from pathlib import Path
from datetime import datetime, timedelta

from ..utils.terminal import display_error


class ConnectionModel(BaseModel):
    """Model for the connection to the database."""

    host: str
    port: int
    user: str
    password: str
    database: str


class LLMUsageDatabaseService:
    """Service for the management of LLM usage on a SQLite database."""

    def __init__(self, connection: ConnectionModel):
        """Initialize the database class.

        Args:
            connection (ConnectionModel): The connection to the database.
        """
        self.connection = connection
        self.mysql_client = None
        self.connected = False

    def start(self):
        """Start the connection to the database."""
        if self.connected:
            return self.mysql_client

        try:
            self.mysql_client = mysql.connector.connect(
                pool_name="gitmit_pool",
                pool_size=5,
                host=self.connection.host,
                port=self.connection.port,
                user=self.connection.user,
                password=self.connection.password,
                database=self.connection.database,
                raise_on_warnings=False,
            )

            if self.mysql_client is None:
                display_error("Cannot connect to MySQL. Fix it before continue.")
                sys.exit(1)

            self.__create_table()
            self.connected = True
            return self.mysql_client
        except Exception as e:
            display_error(
                f"Unknown error when connecting to MySQL. Fix it before continue. See: {e}"
            )

    def close(self):
        """Close the connection to the database."""
        if self.mysql_client is None:
            return

        if self.connected is False:
            return

        try:
            self.mysql_client.close()
            self.connected = False
        except Exception as e:
            display_error(f"An error occurred while closing the MySQL client: {e}")
            sys.exit(1)

    def __create_table(self):
        """Create the table if it doesn't exist."""
        if self.mysql_client is None:
            display_error("You must start the MySQL client before continue.")
            sys.exit(1)

        try:
            cursor = self.mysql_client.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS `tokens_counter` (
                    `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `year` SMALLINT NOT NULL,
                    `month` TINYINT NOT NULL,
                    `tokens_used` MEDIUMINT NOT NULL,
                    `model` VARCHAR(255) NOT NULL,
                    `crc_model` INT UNSIGNED GENERATED ALWAYS AS (CRC32(model)) STORED
                )
                """
            )

            self.mysql_client.commit()
        except Exception as e:
            display_error(f"An error occurred while creating the table: {e}")
            sys.exit(1)
        finally:
            cursor.close()

    def insert_token_usage(self, tokens_used: int, model: str):
        """Insert the token usage into the table.

        Args:
            tokens_used (int): The number of tokens used.
        """
        timestamp = datetime.now()

        year = timestamp.year
        month = timestamp.month

        if self.mysql_client is None:
            display_error("You must start the MySQL client before continue.")
            sys.exit(1)

        try:
            cursor = self.mysql_client.cursor()

            cursor.execute(
                "INSERT INTO `tokens_counter` (`year`, `month`, `tokens_used`, `model`) VALUES (%s, %s, %s, %s)",
                (year, month, tokens_used, model),
            )

            self.mysql_client.commit()
        except Exception as e:
            display_error(f"An error occurred while inserting the token usage: {e}")
            sys.exit(1)
        finally:
            cursor.close()

    def current_month_tokens_used(self, model: str) -> int:
        """Get the current month tokens used.

        Returns:
            int: The number of tokens used.
        """
        if self.mysql_client is None:
            display_error("You must start the MySQL client before continue.")
            sys.exit(1)

        try:
            cursor = self.mysql_client.cursor(dictionary=True)

            cursor.execute(
                "SELECT SUM(`tokens_used`) as `tokens_used` FROM `tokens_counter` WHERE `year` = %s AND `month` = %s AND (`crc_model` = CRC32(%s) AND `model` = %s)",
                (datetime.now().year, datetime.now().month, model, model),
            )

            token_sum = int(cursor.fetchone()["tokens_used"])
            return token_sum if token_sum is not None else 0
        except Exception as e:
            display_error(
                f"An error occurred while getting the current month tokens used: {e}"
            )
            sys.exit(1)
        finally:
            cursor.close()

    def flush_old_tokens(self):
        """Flush old tokens usage before last 30 days."""
        if self.mysql_client is None:
            display_error("You must start the MySQL client before continue.")
            sys.exit(1)

        try:
            cursor = self.mysql_client.cursor()

            cursor.execute(
                "DELETE FROM `tokens_counter` WHERE `timestamp` < ?",
                (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
            )

            self.mysql_client.commit()
        except Exception as e:
            display_error(f"An error occurred while flushing old tokens: {e}")
            sys.exit(1)
        finally:
            cursor.close()
