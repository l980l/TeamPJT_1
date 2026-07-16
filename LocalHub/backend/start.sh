#!/usr/bin/env bash
# Simple start script for Render (example). Use in Render Start Command: bash start.sh

# default PORT is provided by Render in $PORT
PORT=${PORT:-8000}

# run Uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
