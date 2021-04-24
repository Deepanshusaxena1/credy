# Credy Assignment

## Please execute following commands in order to run the project.
```
$ git clone https://github.com/Deepanshusaxena1/credy
$ virtualenv env
$ source env/bin/activate
$ cd credy
$ pip3 install -r requirements.txt
$ python3 manage.py makemigrations movie_services
$ python3 manage.py migrate
$ python3 manage.py runserver
If your access_token get expired you can regenerate it using api/token/
