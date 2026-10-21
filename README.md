
# VerityDB AI

VerityDB AI is a locally hosted, AI-powered database assistant
built with Python, SQLite, Streamlit, and LM Studio.

It allows users to ask questions about a relational database
in natural language, generate SQL queries, view results,
explore analytics, and export data to CSV.

## Features

- Natural-language to SQL generation
- Local AI inference using Qwen through LM Studio
- Read-only SQLite query execution safeguards
- Interactive dashboard and analytics
- Persistent query results within a user session
- CSV export
- Predefined SQL query explorer

## Technology Stack

- Python
- SQLite
- Streamlit
- Pandas
- LM Studio
- Qwen3 4B Instruct

## How It Works

1. A user asks a question in plain English.
2. A locally hosted AI model generates a SQL query.
3. The query engine validates and executes permitted
   read-only SQL.
4. Results are displayed in the Streamlit interface.
5. Users can export the results to CSV.

## Getting Started

1. Clone this repository.
2. Create a Python virtual environment.
3. Install dependencies:

   pip install -r requirements.txt

4. Initialize the demonstration database:

   python database.py

5. Install LM Studio and load the Qwen3 4B Instruct 2507
   model.
6. Start the LM Studio local API server on port 1235.
7. Launch the application:

   streamlit run app.py

## Security and Limitations

VerityDB includes read-only SQLite execution controls,
table restrictions, and query execution limits.

These safeguards are not a substitute for a full
production security audit.

AI-generated SQL may be syntactically valid but logically
incorrect. Query results should be reviewed before
making important decisions.

The project uses fictional demonstration data.

## Future Improvements

- CSV dataset importing
- Dynamic database schema support
- Expanded automated testing
- Additional reporting and visualization tools

## Project Purpose

Developed as a portfolio project to explore relational
databases, AI integration, SQL security, and interactive
data analysis.
