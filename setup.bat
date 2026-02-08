@echo off
echo ============================================================
echo MailMind Setup Script
echo ============================================================
echo.

echo Checking Python version...
python --version
echo.

echo Installing dependencies...
echo This may take a few minutes...
echo.

pip install --upgrade pip
pip install fastapi uvicorn pydantic pydantic-settings sqlalchemy python-dotenv python-multipart python-dateutil dateparser pytest pytest-asyncio httpx

echo.
echo Installing NLP dependencies...
pip install sentence-transformers numpy

echo.
echo Installing Google Gemini (trying new package first)...
pip install google-genai 2>nul
if errorlevel 1 (
    echo New package not available, installing old package...
    pip install google-generativeai
)

echo.
echo Trying to install ChromaDB (optional)...
pip install chromadb 2>nul
if errorlevel 1 (
    echo ChromaDB installation failed - will use fallback mode
    echo This is OK for demo purposes!
)

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Testing installation...
python simple_test.py

echo.
echo To start the API:
echo   python main.py
echo.
echo To run the full demo:
echo   python nlp_rag/demo.py
echo.
pause
