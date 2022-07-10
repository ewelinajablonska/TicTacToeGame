# TicTacToe Game - backend

## Table of contents
* [General info](#general-info)
* [Prerequisites](#rerequisites)
* [Technologies](#technologies)
* [Build and run](#build-and-run)

## General info
This project is implements the backend for a tic tac toe game (RESTful API).

## Prerequisites
I assume you have installed Python.

## Technologies
Project is created with:
* Python version: 3.8.10
* Django version: 4.0.5
* Git version: 2.25.1
* Docker version 5.0.3

## Build and run
Steps to build a Docker image:

1. Clone this repo
```
git clone https://github.com/ewelinajablonska/TicTacToeGame.git
```

2. Go into root directory:
```
cd TicTacToeGame
```

3. Build the image
```
docker build -t django_drf .
```

3. Run the image's default command, which should start everything up. (Note that the host will actually be a guest if you are using boot2docker, so you may need to re-forward the port in VirtualBox.)
```
docker run -d -p 8000:8000 --name django_app django_drf
```

4. Once everything has started up, you should be able to access the webapp via http://localhost:8080/ on your host machine.
```
open: http://localhost:8000/admin/
```
