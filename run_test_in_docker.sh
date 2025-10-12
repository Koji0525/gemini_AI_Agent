#!/bin/bash
# Dockerネットワーク内でテストを実行

docker run --rm \
  --network gemini_ai_agent_default \
  -v "$(pwd)":/workspace \
  -w /workspace \
  python:3.11-slim \
  bash -c "
    pip install -q playwright aiohttp &&
    playwright install chromium &&
    playwright install-deps &&
    python internal_test.py
  "
