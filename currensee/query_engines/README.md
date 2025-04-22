# Query Engines with Memory using `Workflow` and `QueryPipeline`

In addition to this documentation, you can explore how a query engine is called in the notebooks in `notebooks/query_engines`.

## :gear: Mechanics of llama-index `Workflow`

<details>

To create a workflow, you create a custom class that inherits from `Workflow`.
Each step in the flow is decorated with the `@step` so that type inferences can be made for any received objects from the input and output `Events`.
(Input events are passed to the step, while output events are type hinted with `-> Event:`.)

There are default `StartEvent` and `StopEvent` classes, but other custom classes can be used to pass objects from one step to another.

Unlike a pipeline, with a workflow there is no need to instantiate it to add links between its modules.
We can simply set-up the class with the relevant typed `Event` links, and the DAG will be imputed from the events, making readability significantly better.
There are no longer keys passed implicitly - all objects passed as part of events or the `Context` are explicitly accounted for.

There is also no longer the need to instantiate the workflow with every object needed to complete it.
Any objects needed for the initial step will have to be passed, but objects can be created within a step and passed to subsequent steps.

There is also a `Context` - an object available to all steps - that we can leverage to access information from within any step, regardless of the data passed via the input and output events.

Workflows are set up to **only be run asynchronously**, which is no problem for our endpoints.
The `run()` method is set up to be awaited.

</details>


## Current Workflow Implementations

In this repository, we have implemented the follow categories of workflows:
1. SQL Workflow
2. Vector Workflow

### SQL Workflow

<details>
This workflow uses a [`NLSQLTableQueryEngine`](https://docs.llamaindex.ai/en/stable/api_reference/query_engine/NL_SQL_table/) to query SQL data and synthesize a response to a query using an LLM.

Parameters to customize:
- `<table_name>_table_desc`: This description is specific to the table that the query engine is querying. The value should be different for each SQL workflow that is defined on a different dataset. It should be defined within `workflow_descriptions.py`.
- `text_to_sql_prompt`: This prompt defines how the LLM should convert the initial user query into a SQL query to run on the data. It should be defined within `prompts.py`.
- `response_synthesis_prompt_str`: This prompt defines how the SQL response should be synthesized into meaningful text based on the original user query, the SQL query, and the SQL response. It should be defined within `prompts.py`.
</details>



## Adding a New Data Source
<details>

If you are seeking to use an existing workflow with a new SQL table data source, you must follow the following steps:
1. Add a description of the table to `query_engines/workflow_descriptions.py`
    - This should include a description of all of the columns that may be helpful during querying.
2. Add the table name to the `PostgresTables` enum in `schema/schema.py`
3. Add the table to the `SQL_TABLE_DESC_MAPPING` in `query_engines/workflow_descriptions.py`
4. Then, when you instantiate the SQL workflow, pass this table name as the `table_source` argument when you want to use it.

</details>

## Creating a New Workflow

### Code Structure

Each workflow must have the following files defined:
- `query_engine.py`: Defines one creator function: `create_<workflow_name>_workflow`
- `workflow.py`: Defines the workflow and workflow events, if applicable. 


## Tips

While developing your workflow, it is recommended that you try the following:
* If your prompt is not causing the LLM to behave as expected, try providing the prompt to ChatGPT and ask it how it would refine the prompt for efficient and accurate performance using your model (e.g. gemini 1.5 flash)
* Consider using a model better suited to the specific task (e.g. reasoning vs. retrieval)




