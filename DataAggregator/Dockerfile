FROM python:3.8

WORKDIR /app

COPY DataAggregator/main.py /app/main.py
COPY MetricsService/controller.py /app/controller.py

RUN pip install pytz PyGithub pymongo schedule

# Run the script when the container starts
CMD ["python", "main.py"]