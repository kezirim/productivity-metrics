FROM python:3.8

WORKDIR /app

COPY DataAggregator/main.py /app/main.py
COPY MetricsService/controller.py /app/controller.py
COPY set_environment_variables.sh /app/set_environment_variables.sh

RUN chmod +x /app/set_environment_variables.sh

RUN /app/set_environment_variables.sh && rm -f /app/set_environment_variables.sh

RUN pip install PyGithub pymongo schedule

# Run the script when the container starts
CMD ["python", "main.py"]