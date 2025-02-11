set -o errexit

# Actualizar pip
pip install --upgrade pip setuptools

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py makemigrations --noinput
python manage.py migrate --noinput