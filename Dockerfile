
FROM python:2.7-slim

WORKDIR /bot

COPY . /bot

RUN pip install -r requirements.txt

EXPOSE 80

ENV NAME TechStuff

CMD ["python", "bot.py"]


