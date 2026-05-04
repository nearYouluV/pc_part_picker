"""Database initialization script - creates tables and admin user"""
import os
import hashlib
from pathlib import Path
from sqlalchemy import inspect, text
from app.database import engine, SessionLocal
from app.models.base import Base
from app.models.user import User
from app import models  # noqa: F401
from app.services.auth_service import get_password_hash, get_user_by_username
from app.logging_config import get_logger

logger = get_logger(__name__)


def ensure_migration_table(conn):
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            filename VARCHAR(255) PRIMARY KEY,
            checksum VARCHAR(64) NOT NULL,
            applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        )
    """))


def get_applied_migrations(conn) -> dict[str, str]:
    rows = conn.execute(text("SELECT filename, checksum FROM schema_migrations")).fetchall()
    return {row[0]: row[1] for row in rows}


def table_exists(table_name: str) -> bool:
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def column_exists(table_name: str, column_name: str) -> bool:
    inspector = inspect(engine)
    if not table_exists(table_name):
        return False
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def run_migrations():
    migrations_dir = Path(__file__).parent.parent / "migrations"

    if not migrations_dir.exists():
        logger.warning(f"Migrations directory not found: {migrations_dir}")
        return

    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        logger.info("No migration files found")
        return

    logger.info(f"Found {len(migration_files)} migration file(s)")

    with engine.begin() as conn:
        ensure_migration_table(conn)
        applied = get_applied_migrations(conn)

    for migration_file in migration_files:
        filename = migration_file.name
        sql_content = migration_file.read_text()
        checksum = hashlib.sha256(sql_content.encode("utf-8")).hexdigest()
        if filename in applied:
            if applied[filename] != checksum:
                logger.warning(
                    "Migration %s already marked as applied but checksum changed",
                    filename,
                )
            else:
                logger.info("Skipping already applied migration: %s", filename)
            continue

        logger.info(f"Running migration: {migration_file.name}")
        try:
            # Execute each migration in its own transaction so one failure
            # does not abort the rest of the migration chain.
            with engine.begin() as conn:
                conn.exec_driver_sql(sql_content)
                conn.execute(
                    text("""
                        INSERT INTO schema_migrations (filename, checksum)
                        VALUES (:filename, :checksum)
                    """),
                    {"filename": filename, "checksum": checksum},
                )
            logger.info(f"Migration {migration_file.name} completed successfully")
        except Exception as e:
            logger.warning(f"Migration {migration_file.name} error (may already be applied): {e}")


def create_tables():
    logger.info("Checking database tables...")

    if not table_exists("users"):
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    else:
        logger.info("Database tables already exist")

    run_migrations()


def create_admin_user():
    db = SessionLocal()
    try:
        admin_username = os.getenv("ADMIN_USERNAME")
        admin_password = os.getenv("ADMIN_PASSWORD")
        admin_email = os.getenv("ADMIN_EMAIL")

        if not admin_username or not admin_password:
            logger.warning(
                "ADMIN_USERNAME or ADMIN_PASSWORD not set in environment variables. "
                "Skipping admin user creation."
            )
            return

        existing_user = get_user_by_username(db, admin_username)

        if existing_user:
            logger.info(f"Admin user '{admin_username}' already exists; syncing credentials")
            existing_user.email = admin_email
            existing_user.hashed_password = get_password_hash(admin_password)
            existing_user.is_active = True
            existing_user.is_superuser = True
            db.commit()
            logger.info(f"Admin user '{admin_username}' updated successfully")
        else:
            logger.info(f"Creating admin user '{admin_username}'...")
            hashed_password = get_password_hash(admin_password)
            admin_user = User(
                email=admin_email,
                username=admin_username,
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            logger.info(f"Admin user '{admin_username}' created successfully")

    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


def init_database():
    create_tables()
    create_admin_user()
    logger.info("Database initialization complete")


if __name__ == "__main__":
    init_database()
