@echo off
echo Iniciando Jarvis...

start "Backend" cmd /k "cd /d C:\Users\Administrator\Desktop\JARVIS && C:\Users\Administrator\AppData\Local\Python\pythoncore-3.14-64\python.exe -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3

start "Automacoes" cmd /k "cd /d C:\Users\Administrator\Desktop\JARVIS && C:\Users\Administrator\AppData\Local\Python\pythoncore-3.14-64\python.exe automacoes.py"

timeout /t 3

start "Interface" cmd /k "cd /d C:\Users\Administrator\Desktop\JARVIS\jarvis-ui && set HOST=0.0.0.0&& npm start"
echo Jarvis iniciado!