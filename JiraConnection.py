import requests
from requests.sessions import Session
import streamlit as st
from typing import Dict, Union, List, Any
from streamlit.connections import ExperimentalBaseConnection
import json
import pandas as pd
from requests.exceptions import HTTPError


class JiraConnection(ExperimentalBaseConnection[requests.Session]):
    """
    A custom Streamlit connection for interacting with the Jira API using the `requests` library.

    Parameters:
        connection_name (str): The name of the connection.
        base_url (str): The base URL of the Jira instance (e.g., "https://your-jira-instance.atlassian.net").
        **kwargs: Additional keyword arguments to be passed to the parent class constructor.

    Attributes:
        base_url (str): The base URL of the Jira instance.

    Raises:
        ValueError: If invalid or missing credentials are provided.

    Example:
        jira_connection = JiraConnection(
            connection_name="my_jira",
            base_url="https://your-jira-instance.atlassian.net",
            credentials={"username": "your_username", "password": "your_password"},
        )
    """  # noqa: E501

    def __init__(self, connection_name: str, base_url: str, **kwargs):
        self.base_url = base_url
        super().__init__(connection_name, **kwargs)

    def _connect(self, **kwargs) -> Session:
        """
        Establishes a connection to the Jira API using the provided credentials.

        Parameters:
            **kwargs: Additional keyword arguments.

        Returns:
            Session: A new requests.Session object with authentication credentials.

        Raises:
            ValueError: If invalid or missing credentials are provided.

        Example:
            # Connecting with valid credentials
            session = self._connect(credentials={"username": "your_username", "password": "your_password"})
        """  # noqa: E501
        if "credentials" in kwargs:
            credentials = kwargs.pop("credentials")
        else:
            credentials = st.secrets["credentials"]
        username = credentials["username"]
        password = credentials["password"]
        if credentials and username and password:
            session = requests.Session()
            session.auth = (username, password)
            return session
        else:
            raise ValueError("ERROR: Invalid or missing credentials")

    def cursor(self):
        """
        Returns the underlying requests.Session object used for making API requests.

        Returns:
            Session: The underlying requests.Session object.

        Example:
            # Getting the cursor to make direct API requests
            session = jira_connection.cursor()
        """
        return self._instance

    def query(
        self, endpoint: str, params: Dict[str, Any] = None, ttl=600, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Executes an API GET request to the specified Jira endpoint.

        Parameters:
            endpoint (str): The API endpoint to be appended to the base URL.
            params (Dict[str, Any], optional): Query parameters to be sent with the request.
            ttl (int, optional): Time to live in seconds for caching the response (default: 600 seconds).
            **kwargs: Additional keyword arguments.

        Returns:
            List[Dict[str, Any]]: The JSON response data as a list of dictionaries.

        Example:
            # Querying the Jira API for all projects
            projects = jira_connection.query(endpoint="/rest/api/3/project")
        """  # noqa: E501

        @st.cache_data(ttl=ttl)
        def _query(endpoint: str, params: Dict[str, Any] = None, **kwargs):
            url = self.base_url + endpoint
            response = self.cursor().get(url, params=params)
            response.raise_for_status()  # Raise an error if the request fails
            return response.json()

        return _query(endpoint, params, **kwargs)

    def query_projects(
        self, params: Dict[str, Any] = None, ttl=600, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieves a list of Jira projects using the 'query' method.

        Parameters:
            params (Dict[str, Any], optional): Query parameters to be sent with the request.
            ttl (int, optional): Time to live in seconds for caching the response (default: 600 seconds).
            **kwargs: Additional keyword arguments.

        Returns:
            List[Dict[str, Any]]: The JSON response data as a list of project dictionaries.

        Example:
            # Querying Jira API for all projects
            projects = jira_connection.query_projects()
        """  # noqa: E501

        @st.cache_data(ttl=ttl)
        def _query(params: Dict[str, Any] = None, **kwargs):
            url = self.base_url + "/rest/api/3/project"
            response = self.cursor().get(url, params=params)
            response.raise_for_status()
            return response.json()

        return _query(params, **kwargs)

    def query_issue(
        self, issue_id: str, params: Dict[str, Any] = None, ttl=600, **kwargs
    ):
        """
        Retrieves information about a specific Jira issue using the 'query' method.

        Parameters:
            issue_id (str): The ID of the Jira issue to retrieve information about.
            params (Dict[str, Any], optional): Query parameters to be sent with the request.
            ttl (int, optional): Time to live in seconds for caching the response (default: 600 seconds).
            **kwargs: Additional keyword arguments.

        Returns:
            Dict[str, Any]: The JSON response data as a dictionary representing the issue.

        Example:
            # Querying Jira API for information about a specific issue
            issue_id = "ISSUE-123"
            issue_data = jira_connection.query_issue(issue_id)
        """  # noqa: E501

        @st.cache_data(ttl=ttl)
        def _query(params: Dict[str, Any] = None, **kwargs):
            url = self.base_url + "/rest/api/3/issue/" + issue_id
            try:
                response = self.cursor().get(url, params=params)
                response.raise_for_status()
                return response.json()
            except HTTPError as e:  # noqa: F841
                # Handle the 404 error or other HTTP errors
                return None

        return _query(params, **kwargs)

    def query_jql(
        self,
        jql_query: str,
        ttl: int = 600,
        expand=["changelog"],
        fields=["summary", "status"],
        max_results=10,
        start_at=0,
        return_type="count",
        **kwargs,
    ) -> List[Dict[str, Union[str, int]]]:
        """
        Executes a Jira Query Language (JQL) query and retrieves matching issues.

        Parameters:
            jql_query (str): The JQL query string to be executed.
            ttl (int, optional): Time to live in seconds for caching the response (default: 600 seconds).
            expand (List[str], optional): A list of fields to expand in the Jira issue (default: ["changelog"]).
            fields (List[str], optional): A list of fields to include in the search results (default: ["summary", "status"]).
            max_results (int, optional): The maximum number of results to retrieve (default: 10).
            start_at (int, optional): The index of the first result to retrieve (default: 0).
            return_type (str, optional): The type of data to return. Possible values are "count" (returns the total number of issues matching the query),
                                         "json" (returns a list of issue dictionaries), and "dataframe" (returns a Pandas DataFrame of the issues) (default: "count").
            **kwargs: Additional keyword arguments.

        Returns:
            List[Dict[str, Union[str, int]]]: The JSON response data as a list of dictionaries representing the matching issues.

        Raises:
            ValueError: If 'jql_query' is empty or not provided.

        Example:
            # Executing a JQL query to find all issues in a project
            jql_query = 'project = "MYPROJECT"'
            issues = jira_connection.query_jql(jql_query, return_type="json")
        """  # noqa: E501
        if not jql_query:
            raise ValueError("ERROR: 'jql_query' is required")

        @st.cache_data(ttl=ttl)
        def _query(jql_query: str, **kwargs):
            payload = json.dumps(
                {
                    "expand": expand,
                    "fields": fields,
                    "fieldsByKeys": False,
                    "jql": jql_query,
                    "maxResults": max_results,
                    "startAt": start_at,
                }
            )
            try:
                response = self.cursor().post(
                    self.base_url + "/rest/api/3/search",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()  # Raise an exception for non-2xx responses
                data = response.json()
                return data
            except HTTPError as e:
                # Handle the 404 error or other HTTP errors
                return {"error": f"HTTP Error: {e}"}

        if return_type == "count":
            return _query(jql_query, **kwargs)["total"]
        elif return_type == "json":
            return _query(jql_query, **kwargs)["issues"]
        elif return_type == "dataframe":
            issues = _query(jql_query, **kwargs)["issues"]
            df = pd.json_normalize(issues)
            return df
        else:
            return {"error": "Invalid return_type"}
