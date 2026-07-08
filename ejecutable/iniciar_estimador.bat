@echo off
title Estimador COCOMO II
setlocal

echo ==========================================
echo        ESTIMADOR COCOMO II
echo ==========================================
echo.

set "BAT_DIR=%~dp0"
set "PROJECT_DIR=%BAT_DIR%.."

echo Ubicacion del ejecutable:
echo %BAT_DIR%
echo.
echo Cambiando a la raiz del proyecto...
cd /d "%PROJECT_DIR%"
if errorlevel 1 (
    echo ERROR: No se pudo acceder a la raiz del proyecto.
    goto error
)

echo Directorio del proyecto:
echo %CD%
echo.

if not exist "app.py" (
    echo ERROR: No se encontro app.py en la raiz del proyecto.
    echo Verifique que la carpeta ejecutable este dentro del proyecto.
    goto error
)

if not exist "requirements.txt" (
    echo ERROR: No se encontro requirements.txt en la raiz del proyecto.
    goto error
)

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta agregado al PATH.
    echo Instale Python 3 desde:
    echo https://www.python.org/downloads/
    echo.
    echo Durante la instalacion marque la opcion "Add Python to PATH".
    goto error
)

echo Verificando entorno virtual...
if not exist "venv\Scripts\activate.bat" (
    echo Creando entorno virtual en la carpeta venv...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual.
        goto error
    )
) else (
    echo Entorno virtual encontrado.
)

echo.
echo Activando entorno virtual...
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual.
    goto error
)

echo.
echo Actualizando pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: No se pudo actualizar pip.
    goto error
)

echo.
echo Instalando dependencias desde requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias.
    echo Revise su conexion a internet y vuelva a ejecutar este archivo.
    goto error
)

echo.
echo ==========================================
echo        INICIANDO SERVIDOR FLASK
echo ==========================================
echo.
echo La aplicacion se abrira en:
echo http://127.0.0.1:5000
echo.
echo Para detener el servidor presione CTRL + C.
echo.

start http://127.0.0.1:5000

python app.py
if errorlevel 1 (
    echo.
    echo ERROR: La aplicacion finalizo con un problema.
    goto error
)

echo.
echo Servidor finalizado.
pause
exit /b 0

:error
echo.
echo No se pudo iniciar el Estimador COCOMO II.
echo Revise los mensajes anteriores para identificar la causa.
echo.
pause
exit /b 1
