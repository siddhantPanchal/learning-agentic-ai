from dotenv import load_dotenv, dotenv_values
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()


class Information(BaseModel):
    customer: str
    amount: str
    currency: str
    product: str
    relative_date: str


def main():
    client = OpenAI(
        base_url="http://localhost:12434/v1",
    )
    model = dotenv_values()["MODEL"]
    messages = [
        {
            "content": "You are an AI algorithm to extract the details from given input text. user will provide the text and output as valid JSON",
            "role": "system"
        },
        {"content": "John ordered an iPhone 15 yesterday for ₹72,000.", "role": "user"}
    ]

    response = client.responses.parse(model=model,
                                      input=messages,
                                      text_format=Information)

    response_content = response.output_parsed

    # messages.append({"content": response_content, "role": "assistant"})

    print(f"AGENT: > {response_content}")
    pass


if __name__ == '__main__':
    main()
