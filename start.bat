@rem
python --version
python -m venv venv
echo pip install --no-input -r requirements.txt >> .\venv\Scripts\activate.bat
cmd /k  venv\Scripts\activate.bat
