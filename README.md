# Jira Cloud Connector for Streamlit

The `JiraConnection` class is a custom Streamlit connection for interacting with the Jira cloud API using Streamlit's `ExperimentalBaseConnection`.
This class provides a convenient way to connect to Jira, query projects, retrieve issue information, and execute Jira Query Language (JQL) queries. It offers the following features:

1. **Easy Authentication**: The class allows you to provide Jira credentials (username and password/token) during initialization, making it straightforward to authenticate with the Jira API.

2. **Flexible Querying**: You can use the `query` method to execute arbitrary Jira Cloud API endpoints with optional query parameters. This flexibility allows you to interact with various Jira resources effortlessly.

3. **Project and Issue Retrieval**: The `query_projects` and `query_issue` methods provide dedicated functions to fetch lists of Jira projects and retrieve detailed information about specific issues, respectively.

4. **JQL Query Execution**: The `query_jql` method allows you to execute Jira Query Language (JQL) queries to find issues based on various criteria. You can retrieve the total issue count, a list of matching issues, or even a Pandas DataFrame of the results.

### Methods and Usage

The class provides the following methods, each with its specific use case and examples:

1. **_connect**: Establishes a connection to the Jira API with the provided credentials.

2. **cursor**: Returns the underlying `requests.Session` object for direct API access.

3. **query**: Executes an API GET request to the specified Jira endpoint.

4. **query_projects**: Retrieves a list of Jira projects.

5. **query_issue**: Retrieves information about a specific Jira issue.

6. **query_jql**: Executes a Jira Query Language (JQL) query and retrieves matching issues.

Please refer to the [Usage Examples](#example-usage) section for code examples demonstrating how to use each method effectively.

## Example Usage

Below are some examples demonstrating how to use the `JiraConnection` class:

```python
# Create a JiraConnection instance
import streamlit as st
from JiraConnection import JiraConnection
jira_connection = st.experimental_connection(
    "jira", type=JiraConnection, base_url="https://your-jira-instance.atlassian.net"
)

# Query projects
projects = jira_connection.query_projects()
st.json(projects)

# Query a specific issue
issue_id = "ISSUE-123"
issue_data = jira_connection.query_issue(issue_id)
st.json(issue_data)

# Execute a JQL query and retrieve the total count of matching issues
jql_query = 'project = "MYPROJECT"'
issue_count = jira_connection.query_jql(jql_query, return_type="count")
print(f"Total issues found: {issue_count}")

# Execute a JQL query and retrieve the first 10 issues as a Pandas DataFrame
jql_results = jira_connection.query_jql(jql_query, return_type="dataframe")
st.dataframe(jql_results)
```

Remember to replace `"https://your-jira-instance.atlassian.net"` with the actual base URL of your Jira instance, and provide valid Jira credentials when connecting.
