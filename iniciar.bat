@echo off
chcp 65001 > nul
title FastWhisper Web Studio
echo ========================================================
echo         FastWhisper Web Studio - Inicializador
echo ========================================================
echo.

:: Verifica instalacao do Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado no PATH do sistema.
    echo Por favor, instale o Python 3.10 ou superior e tente novamente.
    pause
    exit /b 1
)

:: Verifica se o ambiente virtual existe, senao cria
if not exist ".venv" (
    echo [1/3] Criando ambiente virtual (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao criar o ambiente virtual.
        pause
        exit /b 1
    )
)

:: Ativa o ambiente virtual
call .venv\Scripts\activate.bat

:: Instala / atualiza dependencias
echo [2/3] Verificando dependencias necessarias...
pip install -r requirements.txt --quiet

:: Inicia a aplicacao
echo [3/3] Iniciando FastWhisper Web Studio em http://127.0.0.1:7860...
echo.
echo Pressione CTRL+C nesta janela para encerrar o aplicativo.
echo.

start http://127.0.0.1:7860
python app.py

pause
