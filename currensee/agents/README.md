# LangGraph Agentic Workflow



Current Dummy Flow

           +--------+
           | START |
           +--------+
               |
   +-----------+------------+
   |                        |
   v                        v
+---------------+      +----------------+
| CRM + OUTLOOK |      |     FINNEWS    |
+---------------+      +----------------+
        |                      |
        |                      |
        |                +------------------+
         |               | finnews summary  |
          |              +------------------+
         |                /
          v             v
         +------------+
         | summarizer |
         +------------+

## Testing the Supervisor Agent

To test the end-to-end supervisor agent, use the notebook in `notebooks/agent_development/3.0-gf-complete-graph-testing.ipynb`.

If you would like to test the functionality of a specific tool, use `notebooks/agent_development/2.0-gf-test-tool.ipynb`.


## Using Google GenAI via LangChain

To use, you must have either:

1. The GOOGLE_API_KEY environment variable set with your API key, or

2. Pass your API key using the google_api_key kwarg to the ChatGoogleGenerativeAI constructor.

**NOTE**: The latest models are listed [here](https://ai.google.dev/gemini-api/docs/models).

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
llm.invoke("Write me a ballad about LangChain")

# Invoke

messages = [
    ("system", "Translate the user sentence to French."),
    ("human", "I love programming."),
]
llm.invoke(messages)

# Async

await llm.ainvoke(messages)

# stream:
# async for chunk in (await llm.astream(messages))

# batch:
# await llm.abatch([messages])
```

### Tool Calling

```python
from pydantic import BaseModel, Field


class GetWeather(BaseModel):
    '''Get the current weather in a given location'''

    location: str = Field(
        ..., description="The city and state, e.g. San Francisco, CA"
    )


class GetPopulation(BaseModel):
    '''Get the current population in a given location'''

    location: str = Field(
        ..., description="The city and state, e.g. San Francisco, CA"
    )


llm_with_tools = llm.bind_tools([GetWeather, GetPopulation])
ai_msg = llm_with_tools.invoke(
    "Which city is hotter today and which is bigger: LA or NY?"
)
ai_msg.tool_calls

```


### Embeddings

Using existing embeddings:
```python

from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
embeddings.embed_query("What's our Q1 revenue?")
```


Embed new documents [as follows](https://python.langchain.com/api_reference/google_genai/embeddings/langchain_google_genai.embeddings.GoogleGenerativeAIEmbeddings.html#langchain_google_genai.embeddings.GoogleGenerativeAIEmbeddings.embed_documents):
```python

from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
embeddings.embed_documents(texts, batch_size, task_type, titles, output_dimensionality)
```




