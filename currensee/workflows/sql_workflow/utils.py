from typing import Any

from llama_index.core import SQLDatabase
from llama_index.core.prompts import PromptTemplate
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.workflow import Workflow
from llama_index.llms.google_genai import GoogleGenAI
from currensee.utils.db_utils import create_pg_engine

from currensee.core.settings import Settings
from currensee.schema.models import GoogleModelName
from currensee.schema.schema import PostgresTables
from currensee.workflows.prompts import text_to_sql_tmpl, response_synthesis_prompt_str
from currensee.workflows.sql_workflow.workflow import SqlWorkflow

settings = Settings()


def create_sql_query_engine(
    source_db: str,
    table_description_mapping: dict[str, str],
    text_to_sql_tmpl: str = text_to_sql_tmpl,
    response_synthesis_prompt_str: str= response_synthesis_prompt_str,
    model: GoogleModelName = GoogleModelName.GEMINI_15_FLASH,
    temperature: float = 0.0,
    synthesize_response=True
) -> SqlWorkflow:
    """
    Instantiate SQL workflow and necessary arguments.
    Functionalized to create portability for unit testing
    and future generalized router workflows.

    Parameters
    ----------
    source_db : str
        The database where the tables are located
    table_description_mapping: dict[str,str]
        A mapping between table names and descriptions of the tables to 
        pass to the SQL query engine for it to create SQL queries from
    text_to_sql_tmpl: str, optional
        A prompt describing how to convert the natural language query into a SQL
        query. 
        Defaults to the prompt defined in `prompting.py`
    response_synthesis_prompt_str: str, optional
        A prompt describing how to synthesize the SQL results into a response.
        Defaults to the prompt defined in `prompting.py`
    model : GoogleModelName, optional
        The GEMINI model to use for producing a SQL query from natural language & 
        performing response synthesis - may need to consider separate implementation
        if the same model isn't proficient at both
        Default gemini-1.5-flash
    temperature: float, optional
        Temperature setting to pass to the model
        Default 0.0 (minimal creativity)

    Returns
    -------
    SQLWorkflow
        SQL workflow object
    """


    pg_engine = create_pg_engine(db_name=source_db)

    # Create the prompt that converts text to SQL for querying purposes and synthesizes final response
    text_to_sql_prompt = PromptTemplate(text_to_sql_tmpl)
    response_synthesis_prompt = PromptTemplate(
        response_synthesis_prompt_str
    )

    table_names = list(table_description_mapping.keys())

    # This model performs the reasoning, summary, etc.
    llm = GoogleGenAI(
            model=model,
            temperature=temperature,
            api_key=settings.GOOGLE_API_KEY.get_secret_value()
        )

    # This model creates the embeddings necessary for the retrievers
    embed_model = GoogleGenAI(
            model='models/text-embedding-004',
            temperature=temperature,
            api_key=settings.GOOGLE_API_KEY.get_secret_value()
        )


    # Define the natural language SQL query engine
    # https://docs.llamaindex.ai/en/stable/examples/index_structs/struct_indices/SQLIndexDemo/
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=SQLDatabase(
            pg_engine,
            include_tables=table_names,
            max_string_length=2000,
        ),
        synthesize_response=synthesize_response,
        tables=table_names,
        context_query_kwargs=table_description_mapping,
        text_to_sql_prompt=text_to_sql_prompt,
        llm=llm,
        embed_model=embed_model,
        response_synthesis_prompt=response_synthesis_prompt,

    )

    return sql_query_engine


def create_sql_workflow(
    source_db: str,
    table_description_mapping: dict[str, str],
    text_to_sql_tmpl: str = text_to_sql_tmpl,
    response_synthesis_prompt_str: str= response_synthesis_prompt_str,
    model: GoogleModelName = GoogleModelName.GEMINI_15_FLASH,
    temperature: float = 0.0,
    synthesize_response = True
) -> SqlWorkflow:
    """
    Instantiate SQL workflow and necessary arguments.
    Functionalized to create portability for unit testing
    and future generalized router workflows.

    Parameters
    ----------
    source_db : str
        The database where the tables are located
    table_description_mapping: dict[str,str]
        A mapping between table names and descriptions of the tables to 
        pass to the SQL query engine for it to create SQL queries from
    text_to_sql_tmpl: str, optional
        A prompt describing how to convert the natural language query into a SQL
        query. 
        Defaults to the prompt defined in `prompting.py`
    response_synthesis_prompt_str: str, optional
        A prompt describing how to synthesize the SQL results into a response.
        Defaults to the prompt defined in `prompting.py`
    model : GoogleModelName, optional
        The GEMINI model to use for producing a SQL query from natural language & 
        performing response synthesis - may need to consider separate implementation
        if the same model isn't proficient at both
        Default gemini-1.5-flash
    temperature: float, optional
        Temperature setting to pass to the model
        Default 0.0 (minimal creativity)

    Returns
    -------
    SQLWorkflow
        SQL workflow object
    """


    sql_query_engine = create_sql_query_engine(source_db,
        table_description_mapping,
        text_to_sql_tmpl,
        response_synthesis_prompt_str,
        model,
        temperature,
        synthesize_response=synthesize_response
    )

    run_kwargs: dict[str, Any] = {
        "sql_query_engine": sql_query_engine,
    }

    workflow: Workflow = SqlWorkflow(**run_kwargs, timeout=200.0, verbose=True)

    return workflow