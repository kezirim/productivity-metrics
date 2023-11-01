FROM python:3.8

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt \
    && rm -f requirements.txt

COPY app.py /app/app.py
COPY controller.py /app/controller.py
COPY report_generator.py /app/report_generator.py

EXPOSE 5000

CMD ["python", "app.py"]