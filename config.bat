@echo off    
pip install django
pip install whitenoise 
python -m pip install django-allauth
pip3 install --user django-crispy-forms
pip3 install --user crispy_bootstrap5
pip install django-debug-toolbar 
python -m pip install Pillow
python manage.py runserver
exit /b