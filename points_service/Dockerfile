FROM python:3.10

WORKDIR /

COPY  . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]

EXPOSE 8000
