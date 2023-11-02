"""
This module contains functions for retrieving user's metric from github repositories 
"""
import os
import pytz
import pymongo
from datetime import datetime, timedelta
from github import Github
import logging

logger = logging.getLogger("MetricsLogger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)


MONGO_CONNECTION_STRING = (
    os.environ.get("MONGO_CONNECTION_STRING") or "mongodb://localhost:28000/"
)
METRICS_DATABASE = os.environ.get("METRICS_DATABASE_NAME") or "productivity_metrics"
USER_METRICS_COLLECTION = os.environ.get("USER_METRICS_COLLECTION") or "user_metrics"
HISTORICAL_METRICS_COLLECTION = (
    os.environ.get("HISTORICAL_METRICS_COLLECTION") or "historical_metrics"
)


def get_mongo_client():
    """
    Function returns a MongoDB client

    Parameters:
    None

    Returns:
    object: MongoDB client
    """
    connection_string = MONGO_CONNECTION_STRING
    client = pymongo.MongoClient(connection_string)
    return client


def get_commit_count(username, repo, start_date, end_date):
    """
    Function to compute the number of commits.

    Parameters:
    username (sttring): The Github username.
    repo (object): The object to Github repo.
    start_date (datetime): The start date of metrics collected.
    end_date (datetime): The end date of metrics collected.

    Returns:
    int: number of commits
    """
    commits = 0
    for commit in repo.get_commits():
        commit_date = commit.commit.author.date.replace(tzinfo=pytz.UTC)
        if (
            commit.author
            and commit.author.login == username
            and start_date <= commit_date <= end_date
        ):
            commits += 1
    return commits


def get_lines_of_code(username, repo, start_date, end_date):
    """
    Function to compute the number of lines of code written by a user.

    Parameters:
    username (sttring): The Github username.
    repo (object): The object to Github repo.
    start_date (datetime): The start date of metrics collected.
    end_date (datetime): The end date of metrics collected.

    Returns:
    int: number of lines of code
    """
    lines_of_code = 0
    try:
        contents = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "file":
                file_commits = repo.get_commits(path=file_content.path)
                for commit in file_commits:
                    commit_date = commit.commit.author.date.replace(tzinfo=pytz.UTC)
                    if (
                        commit.author
                        and commit.author.login == username
                        and start_date <= commit_date <= end_date
                    ):
                        lines_of_code += file_content.size
            elif file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
    except Exception as e:
        logger.error(e)
    return lines_of_code


def get_issues_count(repo, start_date, end_date):
    """
    Function to compute the number of open and closed issues.

    Parameters:
    repo (object): The object to github repo.
    start_date (datetime): The start date of metrics collected.
    end_date (datetime): The end date of metrics collected.

    Returns:
    tuple: number of open and closed issues
    """
    issues = repo.get_issues(state="all")
    closed_issues_count = 0
    for issue in issues:
        if issue.created_at >= start_date and issue.created_at <= end_date:
            if issue.state == "closed":
                closed_issues_count += 1
    open_issues_count = issues.totalCount - closed_issues_count
    return (open_issues_count, closed_issues_count)


def get_pull_request_count(repo, start_date, end_date):
    """
    Function to compute the number of open and merged prs.

    Parameters:
    repo (object): The object to github repo.
    start_date (datetime): The start date of metrics collected.
    end_date (datetime): The end date of metrics collected.

    Returns:
    tuple: number of open and closed prs
    """
    pull_requests = repo.get_pulls(state="all", sort="updated", base="master")
    merged_prs_count = 0
    for pr in pull_requests:
        if pr.created_at >= start_date and pr.created_at <= end_date:
            if pr.merged:
                merged_prs_count += 1

    open_prs_count = pull_requests.totalCount - merged_prs_count
    return (open_prs_count, merged_prs_count)


def get_issue_cycle_time(repo, start_date, end_date):
    """
    Function to compute the average issue cycle time.

    Parameters:
    repo (object): The object to github repo.
    start_date (datetime): The start date of metrics collected.
    end_date (datetime): The end date of metrics collected.

    Returns:
    number: average issue cycle time
    """
    issues = repo.get_issues(state="all")
    issue_cycle_times = []
    for issue in issues:
        if (
            issue.closed_at
            and issue.created_at >= start_date
            and issue.closed_at <= end_date
        ):
            cycle_time = issue.closed_at - issue.created_at
            issue_cycle_times.append(
                cycle_time.total_seconds() // (3600 * 24)
            )  # Convert seconds to days

    average_issue_cycle_time = (
        sum(issue_cycle_times) / len(issue_cycle_times) if issue_cycle_times else 0
    )
    return average_issue_cycle_time


def get_code_review_time(repo, start_date, end_date):
    """
    Function to compute code review time (time between a PR being opened and merged)

    Parameters:
    repo (object): The object to github repo.
    start_date (datetime): The start date of metrics collected.
    end_date (datetime): The end date of metrics collected.

    Returns:
    number: average code review time
    """
    pull_requests = repo.get_pulls(state="all", sort="updated", base="master")
    pr_review_times = []
    for pr in pull_requests:
        if pr.merged_at and pr.created_at >= start_date and pr.merged_at <= end_date:
            review_time = pr.merged_at - pr.created_at
            pr_review_times.append(
                review_time.total_seconds() // 60
            )  # Convert seconds to minutes
    average_pr_review_time = (
        sum(pr_review_times) / len(pr_review_times) if pr_review_times else 0
    )
    return average_pr_review_time


def generate_metrics(
    username, repository_name, token=None, start_date=None, end_date=None
):
    """
    Function to generate developer metrics from GitHub using username,
    in combination with other optional args

    Parameters:
    username (str): The object to github repo.
    token (str): The start date of metrics collected.
    start_date (datetime): (Optional) The start date of metrics collected.
    end_date (datetime): (Optional) The end date of metrics collected.

    Returns:
    dict: a collection of developer metrics
    """
    end_date = end_date if end_date else datetime.now()
    start_date = start_date if start_date else end_date - timedelta(weeks=1)

    # make dates to be timezone aware
    start_date = pytz.timezone("UTC").localize(start_date)
    end_date = pytz.timezone("UTC").localize(end_date)

    logger.info("instantiating a GitHub handle...")
    g = Github(token) if token else Github()
    try:
        logger.info("getting GitHub user...")
        user = g.get_user(username)

        logger.info("getting target repository...")
        repo = user.get_repo(repository_name)

        logger.info("collecting metrics...")
        open_issues_count, closed_issues_count = get_issues_count(
            repo, start_date, end_date
        )
        open_prs_count, merged_prs_count = get_pull_request_count(
            repo, start_date, end_date
        )
        issue_cycle_time = get_issue_cycle_time(repo, start_date, end_date)
        code_review_time = get_code_review_time(repo, start_date, end_date)
        commit_count = get_commit_count(username, repo, start_date, end_date)
        lines_of_code = get_lines_of_code(username, repo, start_date, end_date)
        last_modified = pytz.timezone("UTC").localize(datetime.now())

        metrics = {
            "username": username,
            "repository": repository_name,
            "closed_issues": closed_issues_count,
            "open_issues": open_issues_count,
            "merged_prs": merged_prs_count,
            "open_prs": open_prs_count,
            "issue_cycle_time": issue_cycle_time,
            "code_review_time": code_review_time,
            "commits": commit_count,
            "lines_of_code": lines_of_code,
            "start_date": start_date,
            "end_date": end_date,
            "last_modified": last_modified,
        }

        return metrics

    except Exception as e:
        logger.error(e)
        return {"error": str(e)}


def retrieve_metrics(username, repository, token):
    """
    Function to retrieve developer metrics using username and optional token.
    The metrics are retrieved from a database, unless the data is stale (>60 mins)
    and the metrics are retrieved from GitHub directly.

    Parameters:
    username (str): The object to github repo.
    token (str): The start date of metrics collected.

    Returns:
    dict: a collection of developer metrics
    """

    client = get_mongo_client()
    db = client[METRICS_DATABASE]
    collection = db[USER_METRICS_COLLECTION]

    developer_metrics = collection.find_one({"username": username})
    if developer_metrics:
        last_modified = developer_metrics.get("last_modified")
        if last_modified and datetime.now() - last_modified < timedelta(hours=1):
            return developer_metrics

    developer_metrics = generate_metrics(username, repository, token)
    if "error" not in developer_metrics:
        # overwrite stale data
        collection.replace_one({"username": username}, developer_metrics, upsert=True)

    return developer_metrics


def retrieve_historical_metrics(repository, usernames=None):
    """
    Function to retrieve hisorical metrics of a given set of GitHub usernames. Usernames parameter is optional.
    The metrics are retrieved directly from a historical database, which contain weekly metrics snapshots

    Parameters:
    repository (str): The GitHub epository name
    usernames (str): A comma-separated list of GitHub usernames

    Returns:
    dict: a collection of weekly snapshot of productivity metrics
    """
    client = get_mongo_client()
    db = client[METRICS_DATABASE]
    collection = db[HISTORICAL_METRICS_COLLECTION]

    query = {"repository": repository}
    if usernames:
        usernames_list = usernames.split(",")
        query["username"] = {"$in": usernames_list}

    developer_metrics = collection.find(query)
    return developer_metrics
