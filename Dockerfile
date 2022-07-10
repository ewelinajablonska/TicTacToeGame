# Use an official Python runtime as a parent image
FROM python:3.8

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

# create root directory for our project in the container
RUN mkdir /TicTacToeGame

RUN ls .

# Set the working directory to /TicTacToeGame
WORKDIR /TicTacToeGame

# Copy the current directory contents into the container at /TicTacToeGame
ADD . /TicTacToeGame/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

VOLUME /TicTacToeGame

EXPOSE 8000

CMD python manage.py makemigrations && python manage.py migrate && python manage.py createsuperuser && python manage.py runserver 0.0.0.0:8000
