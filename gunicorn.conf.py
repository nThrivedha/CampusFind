"""Gunicorn production configuration file."""
import os

# Render and cloud platforms supply PORT as an environment variable
port = os.environ.get("PORT", "5000")
bind = f"0.0.0.0:{port}"

workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
threads = 4
timeout = 120
keepalive = 5
