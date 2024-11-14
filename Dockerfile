FROM python:3.9
WORKDIR /usr/src/app
COPY . .
RUN mkdir ./images
RUN pip3 install SQLAlchemy pyTelegramBotAPI py-cpuinfo
CMD ["python", "-u", "./main.py"]