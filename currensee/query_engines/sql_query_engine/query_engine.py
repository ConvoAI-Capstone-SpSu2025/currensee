from typing import Any

from llama_index.core import SQLDatabase
from llama_index.core.prompts import PromptTemplate
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.workflow import Workflow
from llama_index.llms.google_genai import GoogleGenAI
from sqlalchemy import create_engine

from currensee.core.settings import Settings
from currensee.schema.models import GoogleModelName
from currensee.schema.schema import PostgresTables
from currensee.query_engines.prompts import text_to_sql_tmpl, response_synthesis_prompt_str
from currensee.query_engines.sql_query_engine.workflow import SqlWorkflow
from currensee.query_engines.workflow_descriptions import SQL_TABLE_DESC_MAPPING

settings = Settings()

def create_sql_workflow(
    source_table: PostgresTables = PostgresTables.CRM_TABLE_ONE,
    model: GoogleModelName = GoogleModelName.GEMINI_15_FLASH,
    temperature: float = 0.0
) -> SqlWorkflow:
    """
    Instantiate SQL workflow and necessary arguments.
    Functionalized to create portability for unit testing
    and future generalized router workflows.

    Parameters
    ----------
    source_table : PostgresTables, optional
        The name of the postgres table to use for querying
        Default crm_table_one (note that this is a placeholder for the real table name)
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


    pg_engine = create_engine(settings.sqlalchemy)

    # Create the prompt that converts text to SQL for querying purposes and synthesizes final response
    text_to_sql_prompt = PromptTemplate(text_to_sql_tmpl)
    response_synthesis_prompt = PromptTemplate(
        response_synthesis_prompt_str
    )

    table_description_mapping = {source_table: SQL_TABLE_DESC_MAPPING[source_table]}


    # Define the natural language SQL query engine
    # https://docs.llamaindex.ai/en/stable/examples/index_structs/struct_indices/SQLIndexDemo/
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=SQLDatabase(
            pg_engine,
            include_tables=[source_table],
            schema=None, #TODO: Define the schema we want to use here
            max_string_length=2000,
        ),
        tables=[source_table],
        context_query_kwargs=table_description_mapping,
        text_to_sql_prompt=text_to_sql_prompt,
        llm=GoogleGenAI(
            model=model,
            temperature=temperature
        ),
        response_synthesis_prompt=response_synthesis_prompt,

    )

    run_kwargs: dict[str, Any] = {
        "sql_query_engine": sql_query_engine,
    }

    workflow: Workflow = SqlWorkflow(**run_kwargs, timeout=200.0, verbose=True)

    return workflow