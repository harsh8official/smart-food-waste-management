"""Application configuration for Smart Food Waste Management System."""

import os


class Config:
    """Centralized Flask, MySQL, upload, and mail settings."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")

    MYSQL_HOST = os.environ.get("MYSQL_HOST") or os.environ.get("MYSQLHOST", "localhost")
    MYSQL_USER = os.environ.get("MYSQL_USER") or os.environ.get("MYSQLUSER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD") or os.environ.get("MYSQLPASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_DB") or os.environ.get("MYSQLDATABASE", "smart_food_waste")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT") or os.environ.get("MYSQLPORT", 3306))
    MYSQL_CURSORCLASS = "DictCursor"

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
