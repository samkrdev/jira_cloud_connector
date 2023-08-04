import streamlit as st
from JiraConnection import JiraConnection
import plotly.express as px


st.set_page_config(layout="wide")

st.markdown("""#### Working with Jira Cloud API using `ExperimentalBaseConnection`""")

tab1, tab2 = st.tabs(["Dashboard", "Credential Setup"])


conn = st.experimental_connection(
    "jira", type=JiraConnection, base_url="https://sam1120.atlassian.net"
)

with tab1:
    st.title("Jira Dashboard")
    st.markdown("### Single Issue view")
    col_issue, col_detail = st.columns(2)

    with col_issue:
        issue_id = st.text_input(
            "Enter an issue ID",
            "test-1",
            help="Enter an issue ID, try test-5 for example",
            placeholder="Enter an issue ID, try test-5 for example",
        )
        st.markdown(
            "Try using `test-5`, `test-6`, `test-7` to test the Single issue view"
        )
    with col_detail:
        if issue_id:
            single_issue = conn.query_issue(f"{issue_id}", ttl=0)
            if single_issue:
                summary = single_issue["fields"]["summary"]
                if single_issue["fields"]["assignee"]:
                    assignee = single_issue["fields"]["assignee"]["displayName"]
                else:
                    # Handle the case when single_issue is None or the keys are missing.
                    assignee = "Unassigned"  # Or any default value that suits your application.  # noqa: E501

                status = single_issue["fields"]["status"]["name"]
                st.dataframe(
                    {"summary": summary, "assignee": assignee, "status": status},
                    width=600,
                )
            else:
                st.error("Issue not found")

    results_df = conn.query_jql(
        "created >= -30d order by created ASC",
        return_type="dataframe",
        fields=["summary", "status", "assignee"],
        ttl=0,
    )
    if len(results_df) > 0:
        issues = results_df[
            [
                "key",
                "fields.summary",
                "fields.status.name",
                "fields.assignee.displayName",
            ]
        ].rename(
            columns={
                "fields.summary": "summary",
                "fields.status.name": "status",
                "fields.assignee.displayName": "assignee",
            }
        )

        status_count = (
            issues.groupby("status").count().reset_index().drop("summary", axis=1)
        )
        st.write("----")
        # Display the results
        st.markdown("### Key Metrics based on the JQL using `JiraConnection.query_jql`")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Issues", value=issues.shape[0])
        with col2:
            st.metric(
                label="Completed",
                value=status_count[status_count["status"] == "Done"]["key"].values[0],
            )
        with col3:
            st.metric(
                label="In Progress",
                value=status_count[status_count["status"] == "In Progress"][
                    "key"
                ].values[0],
            )

        col5, col6 = st.columns(2, gap="medium")

        with col5:
            st.write("----")
            st.markdown("### Status Breakdown")
            fig = px.pie(status_count, values="key", names="status", width=600)
            fig.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.1,
                    xanchor="center",
                    x=0.5,
                    bgcolor="rgba(0, 0, 0, 0)",
                )
            )
            st.plotly_chart(fig, use_container_width=True)
        with col6:
            st.write("----")
            st.markdown("### Unassigned Backlog")
            st.dataframe(
                issues[issues["assignee"].isnull()].drop("assignee", axis=1),
                width=600,
            )
    else:
        st.error("No issues found")
with tab2:
    st.title("Credential setup")
    st.markdown("### Using kwargs")
    st.code(
        """
conn = st.experimental_connection(
    "jira",
    type=JiraConnection,
    base_url="https://jira_wbsite.atlassian.net",
    credentials={
        "username": "user@email.com",
        "password": "password_or_api_token",
    },
)
""",
        language="python",
    )

    st.markdown("### Using streamlit secrets")
    st.code(
        """
[credentials]
username = "user@email.com" # email id of the jira user
password = "password_or_api_token" # password or api token of the jira user
""",
        language="toml",
    )
