
# Load testing tool: Locust, K6

---

- status: accepted
- supersedes: -
- superseded by: -
- date: 2024-09-04
- author: @acaceres
- approval level: low
- coordinated with: @dtroeder (arch), Nubus dev team
- source: https://git.knut.univention.de/univention/customers/dataport/team-souvap/-/issues/560
- scope: ADR is only valid in the Nubus team / Nubus for Kubernetes project. A future ADR may coordinate with the other development teams.
- resubmission: -

---

## Context and Problem Statement

We want a load testing tool we can trust, so we can focus on writing tests

## Considered Options

- [Locust](https://locust.io/)
- [K6](https://k6.io/)

## Pros and Cons of the Options

### Locust

Locust is an open source performance/load testing tool for HTTP and other protocols.

- Good, because the tests are defined using Python
- Good, because it's distributed and scalable - supports hundreds of thousands of concurrent users
- Good, because it has a user-friendly web interface that shows the progress of your test in real-time
- Good, because it supports exporting results in various formats, and integrates with external tools like StatsD for enhanced visibility
- Good, because it can also be run without the UI, making it easy to use for CI/CD testing
- Good, because it's proven and battle tested
- Good, because it's simple and easy to use
- Good, because some experience exists in Univention

*Example of the test:*

```python
from locust import HttpUser, task

class HelloWorldUser(HttpUser):
    host = "http://localhost"
    
    @task
    def hello_world(self):
        self.client.get("/hello")
```

*The command to run the test:*

```shell
locust --headless -u 1 -r 1
```

### K6

K6 is an open-source load testing tool that is designed to be simple and easy to use, with a focus on performance testing of web applications.

- Good, because it's easy to use and has a simple and streamlined command line interface
- Good, because it's lightweight and has a small footprint, which makes it suitable for running large-scale tests
- Good, because it's seamless integration with external services like Grafana and InfluxDB enhances reporting capabilities
- Good, because it's tailored for DevOps and GitLab integration
- Good, because a single instance of k6 can run 30,000-40,000 simultaneous users (VUs)
- Neutral, because it requires some level of knowledge of JavaScript to use effectively
- Bad, because it lacks a graphical user interface for test creation and execution

*Example of the test:*

```javascript
import http from 'k6/http';
import { sleep } from 'k6';

export default function () {
  http.get("http://localhost/hello");
  sleep(1);
}
```

*The command to run the test:*

```shell
k6 run script.js
```

## Decision Outcome

Decision has been taken to proceed with Locust, due to
1) Python compatibility
2) Experience in team
3) Extensibility

## More Information

### Custom Timing and Error Handling in Locust

To track performance metrics for non-HTTP tasks or more complex scenarios, you can utilize the `events.request.fire()`
method in Locust. This method allows you to manually create and send events that are captured by Locust's statistics
system, enabling you to measure custom performance metrics beyond standard HTTP request timings.

#### Important Considerations

**Error Handling**
Please note that Locust does not automatically handle exceptions for custom timings. It is your responsibility
to implement appropriate error handling in your code to ensure accurate metric reporting and to manage any issues
that may arise during execution.
