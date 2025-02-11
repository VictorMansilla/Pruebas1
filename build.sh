set -o errexit

pip install -r requirements.txt

python manage.py makemigrations Usuarios

python manage.py makemigrations Clientes

python manage.py makemigrations Productos

python manage.py migrate
