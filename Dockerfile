FROM python:3.9
WORKDIR /usr/src/app
# COPY . .
RUN mkdir ./images
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# CMD ['docker exec -it py-bot psql -U postgres -d py-bot-db -f /py-bot-db.sql']
# CMD ['docker exec -it py-bot psql postgresql://postgres:postgres@py-bot-postgres:5432/py-bot-db -f /py-bot-db.sql']
# CMD ['docker exec -it py-bot psql postgresql://postgres:postgres@py-bot-db:5432/py-bot-db -f /py-bot-db.sql']
# RUN docker exec -it py-bot psql postgresql://postgres:postgres@py-bot-db:5432/py-bot-db -f /py-bot-db.sql
CMD ["python", "-u", "./main.py"]
# CMD ["python -u ./main.py"]
# RUN docker exec -it py-bot psql postgresql://postgres:postgres@py-bot-db:5432/py-bot-db -f /py-bot-db.sql