
"""
VerityDB AI — Local Model Connection

Connects to a locally hosted language model
through LM Studio's OpenAI-compatible API.
"""
import time
from openai import OpenAI

# Connect to LM Studio running on this computer.
client = OpenAI(
    
base_url="http://127.0.0.1:1235/v1",
    api_key="lm-studio",
    timeout=15.0,
    max_retries=0
)


# Generate SQL from a user's natural-language question.
def generate_sql(question):

    start_time = time.perf_counter()
    response = client.chat.completions.create(
        model="qwen3-4b-instruct-2507",
        messages=[
            {
                "role": "system",
                "content": """
You are an expert SQLite assistant.

Database schema:

departments(
    department_id,
    department_name
)

applications(
    application_id,
    applicant_name,
    department_id,
    status,
    submission_date
)

Relationship:
applications.department_id references departments.department_id.

Valid application statuses:
- Pending
- Approved
- Rejected

Rules:
- Generate a single SQLite SELECT query only.
- Use only the provided tables and columns.
- Preserve the exact capitalization of status values.
- Return only SQL without explanations or Markdown.
"""
            },
            {
                "role": "user",
                "content": question
            }
        ],
        temperature=0,
        max_tokens=200,
        stream=True
    )




   
    first_token_time = None
    sql_parts = []

    for chunk in response:
        if chunk.choices:
            token = chunk.choices[0].delta.content

            if token:
                if first_token_time is None:
                    first_token_time = time.perf_counter()

                sql_parts.append(token)

    total_time = time.perf_counter() - start_time

    if first_token_time is not None:
        wait_time = first_token_time - start_time
        print(f"Time to first token: {wait_time:.2f} seconds")

    print(f"Total AI time: {total_time:.2f} seconds")

    return "".join(sql_parts)
