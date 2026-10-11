from dotenv import load_dotenv
from openai import OpenAI
from openai.types.responses import ResponseTextDoneEvent
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent

load_dotenv()


def main():
    client = OpenAI(
        base_url="http://localhost:12434/v1",
    )
    # model = dotenv_values()["MODEL"]
    model = "docker.io/gemma3:270M-F16"
    messages: list[dict] = [
        # {"content": "Your are an helpful ai agent, user will ask some questions. you need to answer them",
        #  "role": "system"},
    ]

    while True:
        command = input("\nUSER: > ")
        if command == "quit":
            break
        messages.append({"content": command, "role": "user"})
        response = client.responses.create(model=model, input=messages, stream=True)

        print(f"AGENT: > ", end="")
        response_content = ""
        for message in response:
            # print((message))
            if isinstance(message, ResponseTextDeltaEvent):
                print(message.delta, end="")
            if isinstance(message, ResponseTextDoneEvent):
                response_content = message.part["text"]

        messages.append({"content": response_content, "role": "assistant"})

        # print(f"AGENT: > {response_content}")
    pass


if __name__ == '__main__':
    main()
