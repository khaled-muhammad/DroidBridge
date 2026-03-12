"""SQLite database for file index caching."""

import sqlite3
from pathlib import Path
from typing import List, Optional

from models import FileRecord
from utils.logger import get_logger

logger = get_logger(__name__)


class IndexDB:
    """SQLite storage for file records (optional cache)."""

    def __init__(self, db_path: str = "index.db"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """Get or create connection."""
        if self._conn is None:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._create_tables()
        return self._conn

    def _create_tables(self) -> None:
        """Create schema if not exists."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS file_records (
                path TEXT PRIMARY KEY,
                size INTEGER,
                modified_time REAL,
                partial_hash TEXT,
                mime_type TEXT,
                source TEXT,
                index_key TEXT
            )
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_hash ON file_records(partial_hash, size)
        """)
        self._conn.commit()

    def save_records(
        self,
        records: List[FileRecord],
        index_key: str = "default",
    ) -> None:
        """Save records to database."""
        conn = self.connect()
        for r in records:
            conn.execute(
                """INSERT OR REPLACE INTO file_records
                   (path, size, modified_time, partial_hash, mime_type, source, index_key)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    r.path,
                    r.size,
                    r.modified_time,
                    r.partial_hash,
                    r.mime_type,
                    r.source,
                    index_key,
                ),
            )
        conn.commit()
        logger.debug("Saved %d records to DB", len(records))

    def load_records(self, index_key: str = "default") -> List[FileRecord]:
        """Load records from database."""
        conn = self.connect()
        cur = conn.execute(
            "SELECT path, size, modified_time, partial_hash, mime_type, source "
            "FROM file_records WHERE index_key = ?",
            (index_key,),
        )
        return [
            FileRecord(
                path=row["path"],
                size=row["size"],
                modified_time=row["modified_time"],
                partial_hash=row["partial_hash"],
                mime_type=row["mime_type"],
                source=row["source"],
            )
            for row in cur.fetchall()
        ]

    def close(self) -> None:
        """Close connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
