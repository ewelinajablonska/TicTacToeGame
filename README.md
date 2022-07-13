# TicTacToeGame - restful API

## Table of contents
* [General info](#general-info)
* [Prerequisites](#rerequisites)
* [Technologies](#technologies)
* [Build and run](#build-and-run)

## General info
This project is first version of restful API created for the needs of the famous 'tic tac toe' game.

## Prerequisites
I assume you are able to use Windows/Linux/Mac command line or terminal.

## Technologies
Project is created with:
* Python version: 3.8.10
* Django version: 4.0.5

## Build and run
Steps to tun project on local server:

1. Clone this repo
```
git clone https://github.com/ewelinajablonska/TicTacToeGame.git
```

2. Go inside project directory.
```
cd TicTacToeGame
```

3. Acrivate virtual environment.
```
source venv/bin/activate
```

4. Install all necessary packages.
```
pip install -r requirements.txt
```

5. Run all neccessary commands to prepare data base and create admin user.
```
python manage.py migrate
python manage.py createsuperuser
```
```
set all login data:
Username: admin
Email address: admin@example.com
Password: **********
Password (again): *********
Superuser created successfully.
```

## Running
```
python manage.py runserver
```
Login  as superuser at http://127.0.0.1:8000/api/dj-rest-auth/login/

Now you can access http://127.0.0.1:8000/api/

## API Swagger
Api documentation is available at address:

http://127.0.0.1:8000/doc/
