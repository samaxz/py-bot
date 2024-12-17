FROM python:3.9
WORKDIR /app
RUN mkdir ./images
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-u", "./main.py"]
