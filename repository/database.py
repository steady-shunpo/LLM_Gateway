import logging
import os
import sqlite3
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from repository.providerMetricDTO import ProviderMetricsDTO
# if TYPE_CHECKING:

logger = logging.getLogger(__name__)

# Default path for the SQLite database file
DB_PATH = os.getenv("METRICS_DB_PATH", os.path.join(os.path.dirname(__file__), "..", "metrics.db"))


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Create and return a connection to the SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    """Initialize the SQLite database and create the provider_metrics table if not exists."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS provider_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tenant TEXT NOT NULL,
                    final_status TEXT NOT NULL,
                    status_code INTEGER,
                    input_tokens INTEGER DEFAULT 0,
                    output_tokens INTEGER DEFAULT 0,
                    latency REAL DEFAULT 0.0,
                    provider_name TEXT,
                    model TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant TEXT NOT NULL,
                    key TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    revoked BOOLEAN DEFAULT 0
                )
            """)
            conn.commit()
            logger.info("SQLite database initialized at %s", db_path)
    except Exception as e:
        logger.error("Failed to initialize SQLite database: %s", e, exc_info=True)


def save_metric(metric: ProviderMetricsDTO, db_path: str = DB_PATH) -> None:
    """Insert a single ProviderMetricsDTO record into SQLite."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO provider_metrics (
                    tenant, final_status, status_code, input_tokens, output_tokens, latency, provider_name, model
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.tenant,
                metric.final_status,
                metric.status_code,
                metric.input_tokens,
                metric.output_tokens,
                metric.latency,
                metric.provider_name,
                metric.model,
            ))
            conn.commit()
    except Exception as e:
        logger.error("Failed to save metric to SQLite: %s", e, exc_info=True)


def save_metrics(metrics: List[ProviderMetricsDTO], db_path: str = DB_PATH) -> None:
    """Insert a list of ProviderMetricsDTO records in batch into SQLite."""
    if not metrics:
        return
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO provider_metrics (
                    tenant, final_status, status_code, input_tokens, output_tokens, latency, provider_name, model
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    m.tenant,
                    m.final_status,
                    m.status_code,
                    m.input_tokens,
                    m.output_tokens,
                    m.latency,
                    m.provider_name,
                    m.model,
                )
                for m in metrics
            ])
            conn.commit()
    except Exception as e:
        logger.error("Failed to batch save metrics to SQLite: %s", e, exc_info=True)


def get_all_metrics(limit: int = 100, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Retrieve recent metrics records from SQLite."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, tenant, final_status, status_code,
                       input_tokens, output_tokens, latency, provider_name, model
                FROM provider_metrics
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error("Failed to fetch metrics from SQLite: %s", e, exc_info=True)
        return []
