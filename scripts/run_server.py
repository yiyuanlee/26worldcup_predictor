#!/usr/bin/env python3
"""启动 Web 服务（API + 前端）。"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn
from src.config import API_HOST, API_PORT

if __name__ == "__main__":
    reload = os.getenv("API_RELOAD", "0") == "1"
    print(f"启动服务: http://localhost:{API_PORT}")
    uvicorn.run(
        "src.api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=reload,
    )
