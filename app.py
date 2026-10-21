
"""
VerityDB AI
Author: Jorge Francisco-Chavez

Private AI-powered database intelligence platform.
"""

import time
import sqlite3

import pandas as pd
import streamlit as st

from ai import generate_sql
from query_engine import run_query, DATABASE_PATH


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="VerityDB AI",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)


# --------------------------------------------------
# Load database records
# --------------------------------------------------

@st.cache_data(ttl=60)
def load_data():

    connection = sqlite3.connect(
        DATABASE_PATH.as_uri() + "?mode=ro",
        uri=True
    )

    try:
        applications = pd.read_sql_query("""
            SELECT
                a.application_id,
                a.applicant_name,
                d.department_name,
                a.status,
                a.submission_date
            FROM applications AS a
            INNER JOIN departments AS d
                ON a.department_id = d.department_id
            ORDER BY a.application_id
        """, connection)

        analytics = pd.read_sql_query("""
            SELECT
                d.department_name,
                a.status,
                COUNT(*) AS application_count
            FROM applications AS a
            INNER JOIN departments AS d
                ON a.department_id = d.department_id
            GROUP BY d.department_name, a.status
            ORDER BY d.department_name, a.status
        """, connection)

        return applications, analytics

    finally:
        connection.close()


df, analytics_df = load_data()


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("VerityDB AI")

st.caption(
    "Private database intelligence | "
    "Locally hosted AI | Read-only SQL execution"
)

st.divider()


# --------------------------------------------------
# Summary metrics
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Applications", len(df))

with col2:
    st.metric("Departments", df["department_name"].nunique())

with col3:
    st.metric(
        "Pending",
        (df["status"] == "Pending").sum()
    )

with col4:
    st.metric(
        "Approved",
        (df["status"] == "Approved").sum()
    )


# --------------------------------------------------
# Main navigation
# --------------------------------------------------

tab_ai, tab_dashboard, tab_analytics, tab_sql = st.tabs([
    "AI Assistant",
    "Dashboard",
    "Analytics",
    "SQL Explorer"
])



# --------------------------------------------------
# AI Assistant
# --------------------------------------------------

with tab_ai:

    st.subheader("Ask VerityDB")

    st.write(
        "Ask questions about your database in plain English. "
        "VerityDB uses a locally hosted AI model to generate "
        "and execute permitted read-only SQL queries."
    )

    # Store the last successful query and results.
    # Session state survives normal Streamlit reruns.
    if "ai_results" not in st.session_state:
        st.session_state.ai_results = None

    if "ai_sql" not in st.session_state:
        st.session_state.ai_sql = None

    if "ai_time" not in st.session_state:
        st.session_state.ai_time = None

    if "ai_question" not in st.session_state:
        st.session_state.ai_question = None

    # Suggested questions for new users.
    example_questions = [
        "Show all pending applications.",
        "How many applications does each department have?",
        "Which department has the most rejected applications?",
        "Show each applicant's name, department, and status."
    ]

    selected_example = st.selectbox(
        "Suggested questions",
        ["Write my own question"] + example_questions
    )

    default_question = (
        "" if selected_example == "Write my own question"
        else selected_example
    )

    ai_question = st.text_area(
        "Your question",
        value=default_question,
        placeholder="Ask a question about your database...",
        height=110
    )

    # Generate and execute a query only when requested.
    if st.button(
        "Generate & Execute",
        type="primary",
        key="ask_ai"
    ):

        if not ai_question.strip():
            st.warning("Please enter a question.")

        else:
            try:
                with st.spinner("Generating SQL..."):
                    start_time = time.perf_counter()

                    generated_query = generate_sql(
                        ai_question
                    )

                    ai_time = (
                        time.perf_counter() - start_time
                    )

                with st.spinner("Validating and executing SQL..."):
                    columns, rows = run_query(
                        generated_query
                    )

                results_df = pd.DataFrame(
                    rows,
                    columns=columns
                )

                # Save the successful response in session state.
                st.session_state.ai_results = results_df
                st.session_state.ai_sql = generated_query
                st.session_state.ai_time = ai_time
                st.session_state.ai_question = ai_question

            except ValueError as error:
                st.error(f"Query rejected: {error}")

            except Exception as error:
                st.error(
                    "Unable to complete the request. "
                    "Verify that LM Studio is running."
                )
                st.code(str(error))

    # Display the saved response on every rerun.
    if st.session_state.ai_results is not None:

        st.success("Query completed successfully.")

        st.caption(
            f"AI generation: {st.session_state.ai_time:.2f} seconds | "
            f"Records returned: {len(st.session_state.ai_results)}"
        )

        st.subheader("Query Results")

        st.dataframe(
            st.session_state.ai_results,
            width="stretch",
            hide_index=True
        )

        # Convert the DataFrame to CSV.
        csv_data = st.session_state.ai_results.to_csv(
            index=False
        ).encode("utf-8")

        # Allow users to download their query results.
        st.download_button(
            label="Download Results (CSV)",
            data=csv_data,
            file_name="veritydb_query_results.csv",
            mime="text/csv",
            key="download_ai_results"
        )

        with st.expander("View generated SQL"):
            st.code(
                st.session_state.ai_sql,
                language="sql"
            )



# --------------------------------------------------
# Dashboard
# --------------------------------------------------

with tab_dashboard:

    st.subheader("Application Records")

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:

        selected_department = st.selectbox(
            "Department",
            ["All Departments"] +
            sorted(df["department_name"].unique())
        )

    with filter_col2:

        selected_status = st.selectbox(
            "Status",
            [
                "All Statuses",
                "Pending",
                "Approved",
                "Rejected"
            ]
        )

    filtered_df = df.copy()

    if selected_department != "All Departments":

        filtered_df = filtered_df[
            filtered_df["department_name"]
            == selected_department
        ]

    if selected_status != "All Statuses":

        filtered_df = filtered_df[
            filtered_df["status"]
            == selected_status
        ]

    st.dataframe(
        filtered_df,
        width="stretch",
        hide_index=True
    )

    st.caption(
        f"Showing {len(filtered_df)} of {len(df)} applications"
    )


# --------------------------------------------------
# Analytics
# --------------------------------------------------

with tab_analytics:

    st.subheader("Application Analytics")

    st.write(
        "Application distribution by department and status."
    )

    chart_df = analytics_df.pivot(
        index="department_name",
        columns="status",
        values="application_count"
    ).fillna(0)

    st.bar_chart(chart_df)

    st.subheader("Detailed Breakdown")

    st.dataframe(
        analytics_df,
        width="stretch",
        hide_index=True
    )


# --------------------------------------------------
# SQL Explorer
# --------------------------------------------------

with tab_sql:

    st.subheader("SQL Explorer")

    st.write(
        "Explore predefined SQL queries and their results."
    )

    questions = {

        "Which departments have the most pending applications?": """
            SELECT
                d.department_name,
                COUNT(a.application_id) AS pending_count
            FROM departments AS d
            LEFT JOIN applications AS a
                ON d.department_id = a.department_id
                AND a.status = 'Pending'
            GROUP BY d.department_id, d.department_name
            ORDER BY pending_count DESC;
        """,

        "How many applications are in each department?": """
            SELECT
                d.department_name,
                COUNT(a.application_id) AS total_applications
            FROM departments AS d
            LEFT JOIN applications AS a
                ON d.department_id = a.department_id
            GROUP BY d.department_id, d.department_name
            ORDER BY total_applications DESC;
        """,

        "How many applications have each status?": """
            SELECT
                status,
                COUNT(*) AS total
            FROM applications
            GROUP BY status
            ORDER BY total DESC;
        """
    }

    selected_question = st.selectbox(
        "Choose a SQL question",
        list(questions.keys())
    )

    if st.button("Run Query", key="sql_explorer"):

        try:

            selected_query = questions[selected_question]

            columns, rows = run_query(selected_query)

            results_df = pd.DataFrame(
                rows,
                columns=columns
            )

            st.subheader("Results")

            st.dataframe(
                results_df,
                width="stretch",
                hide_index=True
            )

            with st.expander("View SQL"):
                st.code(
                    selected_query,
                    language="sql"
                )

        except Exception as error:
            st.error(str(error))


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "VerityDB AI | Python · Streamlit · SQLite · "
    "Local LLM | Fictional demonstration data"
)
