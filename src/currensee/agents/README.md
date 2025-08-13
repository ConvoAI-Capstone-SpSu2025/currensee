# CurrenSee Agent System

This directory contains the agent modules for the CurrenSee platform. Each agent is responsible for a specialized task in the multi-agent orchestration pipeline that powers CurrenSee's meeting intelligence and report generation.

## Overview

CurrenSee uses a modular, agent-based architecture to:
- Retrieve and summarize data from internal (CRM, Outlook) and external (financial news) sources
- Categorize meeting topics and client questions
- Integrate, filter, and summarize information for personalized client reports
- Enforce security and compliance guardrails at each step

## Example Agent Workflow

```
                     +--------+
                     | START  |
                     +--------+
                             |
     +-----------+------------+
     |                        |
     v                        v
 +---------------+      +----------------+
 | CRM + OUTLOOK |      |   FINNEWS      |
 +---------------+      +----------------+
                |                      |
                v                      v
     +----------------+   +------------------+
     | Categorization |   | finnews summary  |
     +----------------+   +------------------+
                |                      |
                 \                    /
                    v                  v
                     +------------+
                     | summarizer |
                     +------------+
```

## Key Agents

- **CRM Agent**: Retrieves and processes CRM data
- **Outlook Agent**: Summarizes recent emails and meetings
- **FinNews Agent**: Pulls and summarizes relevant financial news
- **Categorization Agent**: Determines meeting focus and client questions
- **Summarizer Agent**: Integrates all information into a final report
- **Guardrails Agent**: Applies security, compliance, and tone validation

See the main project README for a full list and workflow diagram.

## Testing Agents

- To test the end-to-end supervisor agent, use the notebook:  
    `notebooks/2.0-agent_development/0.0-capstone_one/3.0-gf-complete-graph-testing.ipynb`
- To test individual tools/agents, use:  
    `notebooks/2.0-agent_development/0.0-capstone_one/2.0-gf-test-tool.ipynb`

## Using Google GenAI via LangChain

Some agents leverage Google Gemini models via LangChain. To use these features, you must:

1. Set the `GOOGLE_API_KEY` environment variable with your API key, or
2. Pass your API key using the `google_api_key` kwarg to the `ChatGoogleGenerativeAI` constructor.

See the [Gemini API model list](https://ai.google.dev/gemini-api/docs/models) for available models.

### Example: Basic Usage

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
llm.invoke("Write me a ballad about LangChain")

# System/human messages
messages = [
        ("system", "Translate the user sentence to French."),
        ("human", "I love programming."),
]
llm.invoke(messages)

# Async
await llm.ainvoke(messages)
```

### Tool Calling Example

```python
from pydantic import BaseModel, Field

class GetWeather(BaseModel):
        '''Get the current weather in a given location'''
        location: str = Field(..., description="The city and state, e.g. San Francisco, CA")

class GetPopulation(BaseModel):
        '''Get the current population in a given location'''
        location: str = Field(..., description="The city and state, e.g. San Francisco, CA")

llm_with_tools = llm.bind_tools([GetWeather, GetPopulation])
ai_msg = llm_with_tools.invoke(
        "Which city is hotter today and which is bigger: LA or NY?"
)
print(ai_msg.tool_calls)
```

### Embeddings Example

```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
embeddings.embed_query("What's our Q1 revenue?")

# Embed new documents
embeddings.embed_documents(texts, batch_size, task_type, titles, output_dimensionality)
```

---

For more details on agent orchestration and the full workflow, see the main [CurrenSee README](../../../README.md).
