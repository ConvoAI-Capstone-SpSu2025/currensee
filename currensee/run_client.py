import asyncio

from currensee.client import AgentClient
from currensee.core import settings
from currensee.schema import ChatMessage


async def amain() -> None:
    #### ASYNC ####
    client = AgentClient(settings.BASE_URL, agent="chatbot", get_info=False)

    # print("Agent info:")
    # print(client.info)

    print("Chat example:")
    response = await client.ainvoke("Tell me a brief joke?")
    response.pretty_print()

    print("\nStream example:")
    async for message in client.astream("Share a quick fun fact?"):
        if isinstance(message, str):
            print(message, flush=True, end="")
        elif isinstance(message, ChatMessage):
            print("\n", flush=True)
            message.pretty_print()
        else:
            print(f"ERROR: Unknown type - {type(message)}")


def main() -> None:
    #### SYNC ####
    client = AgentClient(settings.BASE_URL, agent="chatbot", get_info=False)

    # print("Agent info:")
    # print(client.info)

    print("Chat example:")
    response = client.invoke("Tell me a brief joke?", model="gpt-4o")
    response.pretty_print()

    print("\nStream example:")
    for message in client.stream("Share a quick fun fact?"):
        if isinstance(message, str):
            print(message, flush=True, end="")
        elif isinstance(message, ChatMessage):
            print("\n", flush=True)
            message.pretty_print()
        else:
            print(f"ERROR: Unknown type - {type(message)}")


if __name__ == "__main__":
    print("Running in sync mode")
    main()
    print("\n\n\n\n\n")
    print("Running in async mode")
    asyncio.run(amain())