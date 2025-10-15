@echo off

echo "Verificando se o ambiente virtual existe..."
if not exist venv (
    echo "Criando ambiente virtual..."
    python -m venv venv
)

echo "Ativando o ambiente virtual..."
call venv\Scripts\activate.bat

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Instalando o pre-commit..."
pre-commit install

echo "Instalacao finalizada."
pause