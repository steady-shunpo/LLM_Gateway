import hashlib
import logging
import secrets
from typing import Optional
from repository.database import get_connection

logger = logging.getLogger(__name__)


class keyGenerator:

    # def __init__(self):
    #     with get_connection() as conn:
    #         cursor = conn.cursor()
    #         cursor.execute("""
    #             CREATE TABLE IF NOT EXISTS api_keys (
    #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                 tenant TEXT NOT NULL,
    #                 key TEXT NOT NULL,
    #                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    #                 revoked BOOLEAN DEFAULT 0
    #             )
    #         """)
    #         conn.commit()

    @staticmethod
    def generate_api_key(prefix: str = "sk-", length: int = 32) -> str:
        """
        Generate a cryptographically secure random API key.
        """
        return f"{prefix}{secrets.token_urlsafe(length)}"

    @staticmethod
    def store_key(api_key: str, tenant: str) -> None:
        """
        SHA-256 hash the key and store it with tenant, created_at, and revoked in the api_keys table.
        """
        key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS api_keys (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tenant TEXT NOT NULL,
                        key TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        revoked BOOLEAN DEFAULT 0
                    )
                """)
                cursor.execute("""
                    INSERT INTO api_keys (tenant, key, created_at, revoked)
                    VALUES (?, ?, CURRENT_TIMESTAMP, 0)
                """, (tenant, key_hash))
                conn.commit()
                logger.info("API key stored successfully for tenant: %s", tenant)
        except Exception as e:
            logger.error("Failed to store API key in database: %s", e, exc_info=True)
            raise

    @staticmethod
    def generate_key(tenant: str, prefix: str = "sk-", length: int = 32) -> str:
        """
        Orchestrate generating a new API key, storing its hash in the database,
        and returning the raw key as is.
        """
        api_key = keyGenerator.generate_api_key(prefix=prefix, length=length)
        keyGenerator.store_key(api_key=api_key, tenant=tenant)
        return api_key

    @staticmethod
    def verify_key(api_key: str) -> Optional[str]:
        """
        Compute SHA-256 hash of the provided API key and verify against the database.
        Returns the tenant name if the key is valid and not revoked, otherwise None.
        """
        if not api_key:
            return None
        key_hash = hashlib.sha256(api_key.strip().encode("utf-8")).hexdigest()
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS api_keys (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tenant TEXT NOT NULL,
                        key TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        revoked BOOLEAN DEFAULT 0
                    )
                """)
                cursor.execute("""
                    SELECT tenant FROM api_keys
                    WHERE key = ? AND (revoked = 0 OR revoked IS NULL)
                    ORDER BY id DESC
                    LIMIT 1
                """, (key_hash,))
                row = cursor.fetchone()
                if row:
                    return row["tenant"]
                return None
        except Exception as e:
            logger.error("Failed to verify API key: %s", e, exc_info=True)
            return None

