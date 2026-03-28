"""
Database migrations manager for DevOps Interview Bot

Автоматически применяет миграции к существующей БД.
Idempotent: можно запускать повторно без ошибок.
"""

import sqlite3
import os
from pathlib import Path


def run_migrations(db_path: str = None):
    """
    Run all pending migrations.
    
    Args:
        db_path: Path to SQLite database file. 
                 Defaults to DATABASE_PATH env var or 'data/devops_bot.db'
    """
    if db_path is None:
        db_path = os.getenv("DATABASE_PATH", "data/devops_bot.db")
    
    # Resolve relative paths
    if not os.path.isabs(db_path) and db_path != ':memory:':
        db_path = os.path.abspath(db_path)
    
    print(f"[Migrations] Running migrations on: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Migration 001: Add learning carousel columns
        _migrate_001_learning_columns(cursor, conn)
        
        print("[Migrations] ✅ All migrations completed successfully")
    except Exception as e:
        print(f"[Migrations] ❌ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def _migrate_001_learning_columns(cursor, conn):
    """Migration 001: Add learning_topic and learning_card columns"""
    
    # Check if learning_topic column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'learning_topic' not in columns:
        print("[Migration 001] Adding learning carousel columns...")
        
        # Add learning_topic
        cursor.execute("ALTER TABLE users ADD COLUMN learning_topic VARCHAR(20)")
        
        # Add learning_card
        cursor.execute("ALTER TABLE users ADD COLUMN learning_card INTEGER DEFAULT 1")
        
        conn.commit()
        print("[Migration 001] ✅ Added learning_topic and learning_card columns")
    else:
        print("[Migration 001] ⏭️  Already applied (learning columns exist)")


if __name__ == "__main__":
    # Standalone migration script
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else None
    run_migrations(db_path)
