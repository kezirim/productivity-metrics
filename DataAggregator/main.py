import os
import schedule
import time
from github import Github
import pymongo
from datetime import datetime, timedelta
import controller as Controller

# get MongoDB connection
client = Controller.get_mongo_client()
db = client[Controller.METRICS_DATABASE]
collection = db[Controller.HISTORICAL_METRICS_COLLECTION]
token = Controller.PERSONAL_GITHUB_TOKEN

# retrieve username and repository passed via CMD line
usernames_string = os.environ.get("USERNAMES")
repository_name = os.environ.get("TARGET_REPOSITORY")


def pull_github_metrics():
    # Get the current date and the date a week ago
    # adjust date to UTC
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=1)

    # get token
    usernames = usernames_string.split(",")  # to be provided
    metrics_data = []
    for username in usernames:
        # collect metrics for the current week
        metrics = Controller.generate_metrics(
            username, token, start_date, end_date
        )  # maybe invoke api or reuse module
        metrics_data.append(metrics)
    collection.insert_many(metrics_data)


# Schedule the job to run every week on a specific day (Monday) and time (5:00 am)
schedule.every().monday.at("5:00").do(
    pull_github_metrics
)  # Adjust day and time as needed

# Run the scheduler continuously
while True:
    schedule.run_pending()
    time.sleep(1)
