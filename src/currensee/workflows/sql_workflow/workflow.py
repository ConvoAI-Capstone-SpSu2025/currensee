# llama_index workflow imports
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.workflow import (Context, Event, StartEvent, StopEvent,
                                       Workflow, step)


# Define the workflow
class SqlWorkflow(Workflow):
    """Workflow designed to query a SQL query engine and synthesize a final response.

    Steps involved -
    - Rewrite the original query
    - Query the SQL query engine to get a response
    - Synthesize the response into an intelligible answer and return response object
    """

    def __init__(self, sql_query_engine: NLSQLTableQueryEngine, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sql_query_engine = sql_query_engine

    @step
    async def generate_sql_response(self, ctx: Context, ev: StartEvent) -> StopEvent:
        """
        Querying the SQL query engine

        Parameters
        ----------
        ctx: Context
            Context that is used to pass along information throughout the whole
            workflow. It helps the other steps in the workflow to access important
            arguments
        ev: StartEvent
            The event should contain -
                * query: str - the user query

        Returns
        -------
        SQLResponseEvent : Event
            This event contains -
            * sql_response : Response
                Response object from the SQL query engine
            * sql_query : str
                The SQL statement returned as metadata
        """
        user_query = ev.query

        # Query the SQL query engine
        sql_response = await self.sql_query_engine.aquery(user_query)
        sql_response.metadata["user_query"] = user_query
        sql_query = sql_response.metadata["sql_query"] if sql_response.metadata else ""

        return StopEvent(result=sql_response)
