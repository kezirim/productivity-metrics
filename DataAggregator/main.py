import os
import schedule
import time
from github import Github
from datetime import datetime, timedelta
import controller as Controller

logger = Controller.logger

# get MongoDB connection
client = Controller.get_mongo_client()
db = client[Controller.METRICS_DATABASE]
collection = db[Controller.HISTORICAL_METRICS_COLLECTION]

# retrieve username and repository passed via CMD line
usernames_string = os.environ.get("USERNAMES")
repository_name = os.environ.get("TARGET_REPOSITORY")
token = os.environ.get("PERSONAL_GITHUB_TOKEN")


def pull_github_metrics():
    try:
        # Get the current date and the date a week ago
        # adjust date to UTC
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=1)

        # get token
        usernames = usernames_string.split(",")  # to be provided
        metrics_data = []
        for username in usernames:
            # collect metrics for the current week
            logger.info("Generaing metrics")
            metrics = Controller.generate_metrics(
                username=username,
                repository_name=repository_name,
                token=token,
                start_date=start_date,
                end_date=end_date,
            )
            if "error" in metrics:
                logger.error(metrics["error"])
            else:
                metrics_data.append(metrics)
        logger.info("Inserting results in database")
        collection.insert_many(metrics_data)
    except Exception as e:
        logger.error(e)


# Schedule the job to run every week on a specific day (Monday) and time (7:00 am)
schedule.every().monday.at("07:00").do(
    pull_github_metrics
)  # Adjust day and time as needed

# Run the scheduler continuously
while True:
    schedule.run_pending()
    time.sleep(1)
