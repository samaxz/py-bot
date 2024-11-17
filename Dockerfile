FROM python:3.9
WORKDIR /usr/src/app
COPY . .
RUN mkdir ./images
RUN pip install --upgrade pip
RUN pip3 install sqlalchemy pytelegrambotapi py-cpuinfo psutil psycopg2
CMD ["python", "-u", "./main.py"]