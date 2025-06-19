text_to_sql_tmpl = """
    Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
    You can order the results by the find_date column (from earliest to latest) to return the most interesting examples in the database.

    GUIDELINES:
    * Never query for all the columns from a specific table, only ask for a few relevant columns given the question.
    * Pay attention to use only the column names that you can see in the schema description.
    * Be careful to not query for columns that do not exist.
    * Pay attention to which column is in which table.
    * Make sure to filter on all criteria mentioned in the query.
    * If using a LIMIT to restrict the results, make sure it comes only in the end of the query.

    IMPORTANT NOTE:
    * Use the ~* operator instead of = when filtering with WHERE on text columns.
    * Add word boundaries '\y' to the beginning and end of each search term in the query.

    You are required to use the following format, each taking one line:

    Question: Question here
    SQLQuery: SQL Query to run
    SQLResult: Result of the SQLQuery
    Answer: Final answer here

    Only use tables listed below.
    {schema}

    Question: {query_str}
    SQLQuery:
"""


response_synthesis_prompt_str = """

    Query: {query_str}
    SQL: {sql_query}
    SQL Response: {context_str}

    IMPORTANT INSTRUCTIONS:
    * If SQL Response is empty or 0, apologise and mention that you could not find
     examples to answer the query.
    * In such cases, kindly nudge the user towards providing more details or refining
    their search.
    * Additionally, you can tell them to rephrase specific keywords.
    * Do not explicitly state phrases such as 'based on the SQL query executed' or related
     references to context in your Response.
    * Never mention the underlying sql query, or the underling sql tables and other database elements
    * Never mention that sql was used to answer this question

    Considering the IMPORTANT INSTRUCTIONS above, create an response using the information
    returned from the database and no prior knowledge.


    Response:
"""
