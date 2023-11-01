# Developer Productivity

This project aims to track the evolving productivity of individual engineers/contributors in a team over time using metrics obtained from a Github repository.

Relying solely on GitHub metrics for measuring productivity is counterproductive. These metrics reflect tool impact rather than individual performance or teamwork efficiency. Team performance is better assessed using established DORA metrics like deployment frequency, lead time changes, time to restore services, and failure rate changes. However, measuring individual developer productivity in isolation from the team can lead to:

1. Unhealthy competition, encouraging gaming the system.
2. Inability to capture vital contributions like mentoring, coaching, pair programming, and creative brainstorming.
3. Rushed solutions undermining the creativity needed for efficient software.
4. Deterring risk-taking in process optimization and code efficiency.
5. Encouraging risk-averse behavior to maintain a good performance score.

## Assumptions

Productivity, as defined here, comprises a combination of the following metrics. Teams have the flexibility to prioritize these metrics based on their significance or assign specific weights to each. The included metrics in this solution are:

- Number of commits
- Lines of code
- Open Pull Requests
- Merged Pull Requests
- Open Issues
- Closed Issues
- Issue Cycle Time
- Code Review Time

These productivity metrics are collected on a weekly basis instead of on a daily basis. Collecting productivity metrics on a weekly basis as opposed to a daily basis involves a trade-off between storage performance and the time required to observe significant changes in productivity. Daily collection of productivity metrics can generate a larger volume of data, thus requiring more storage capacity, which can become a concern, especially if the system scales.

Daily data points might offer more granular insights into productivity changes, capturing smaller fluctuations. However, these changes might be insignificant and not reflective of actual productivity shifts, leading to noise in the data. Weekly metrics tend to smooth out daily fluctuations, making it easier to identify trends and significant changes in productivity over a longer timeframe, thus providing a clearer picture of actual shifts in productivity.

## Project Overview

This project comprises 3 modules: MetricsService, DatabaseInstantiator, DataAggregator.

### MetricsService

The module provides a robust REST API service designed for retrieving productivity metrics and generating reports based on the stored data. Key functions include:

- Retrieval of productivity metrics for a specified user via their Github username and repository name. This function optimizes performance through a caching mechanism. It queries the Github repository only if the stored metrics in the database are more than one hour old, updating the database with fresh metrics collected from Github.

- Generation of reports in various formats such as CSV, text, or PDF, containing the productivity metrics of a user. The report type is specified by the user and can be customized based on the username provided.

- Creation of historical reports depicting trends over time for one or more developers, using a list of usernames. The data utilized in this report is compiled from the information collected by the DataAggregator service.

To launch the service, execute the following command from the command line: `python MetricsService/app.py`

Additionally, the service can be containerized using the included Dockerfile. To do so:

Build the Docker image using the command:

```
docker build -t metrics-service .
```

Run the Docker container via:

```
docker run -d -p 5000:5000 metrics-service
```

This service offers a powerful set of functionalities, facilitating metric retrieval, report generation, and historical trend analysis, and can be easily deployed as a Docker container for efficient and scalable usage.

### DataAggregator

A Docker-contained service runs continuously, aggregating metrics by extracting data from GitHub using a specified list of usernames and repositories. These metrics are gathered on a weekly schedule and stored in a MongoDB database, which is set up and managed by the DatabaseInstantiator.

To build the Docker container, execute the command below:

```
docker build -t data_aggregator -f DataAggregator/Dockerfile .
```

To run the container, use the command:

```
docker run -d -e USERNAMES=dev1,dev2,dev3 -e TARGET_REPOSITORY=<repository name> data_aggregator
```

This Docker containerization creates a persistent service dedicated to metric aggregation from GitHub, collecting and storing data in a MongoDB database facilitated by the DatabaseInstantiator setup.

### DatabaseInstantiator

This module consist of a Python script that provisions a Docker volume to persist a MongoDB database and initializes it using the latest mongo container. Both MetricService and DataAggregator produce metrics stored within this database.

However, the implementation utilizing Docker volumes might introduce performance bottlenecks and management complexities, tethering the solution to Docker and potentially leading to vendor lock-in. Enhancing this setup could involve exploring an independent, non-Docker-based database solution for better performance and reduced dependency on a specific platform.

To launch the DatabaseInstantiator, execute the following command from the command line:

```
python setup.py
```
