pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
echo "from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.filter(email='admin@gmail.com').exists() or User.objects.create_superuser(email='admin@gmail.com', password='admin123', first_name='Admin', last_name='User')" | python manage.py shell