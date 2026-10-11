import asyncio

from dotenv import load_dotenv, dotenv_values

load_dotenv()
from langchain.chat_models import init_chat_model

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda

model_name = dotenv_values()["MODEL"] or ""
base_url = dotenv_values()["BASE_URL"] or ""

# client = ChatOpenAI(base_url=base_url, model=model_name)
client = init_chat_model(model=model_name, base_url=base_url, model_provider="openai")
parser = StrOutputParser()


def print_msg(msg: str):
    return lambda x: print_output(msg, x)


def print_output(msg: str, input_text: str) -> str:
    print(f"{msg} {input_text}")
    return input_text


async def main():
    base_prompt = "Tell me about Redis"

    research_aggregator = (
            RunnableLambda(print_msg("Extracting Key from ")) |
            RunnableParallel(
                {
                    "keyword": ChatPromptTemplate.from_template(
                        "give me keyword of `{prompt}` prompt, just tell me in 1 or 2 word") | client | parser
                }
            )
            | RunnableLambda(print_msg("Researching on : "))
            |
            RunnableParallel({
                "technical_aspect": ChatPromptTemplate.from_template(
                    "Give technical aspect of {keyword}") | client | parser,
                "key_features": ChatPromptTemplate.from_template(
                    "Give key features {keyword}") | client | parser,
                "potential_drawbacks": ChatPromptTemplate.from_template(
                    "Give potential drawbacks {keyword}") | client | parser,
            })
            # | RunnableLambda(print_msg("Preparing the report : \n"))
            |
            ChatPromptTemplate.from_template(
                "Synthesize this research into a summary report based on technical aspect: {technical_aspect}, key features: {key_features}, potential drawbacks: {potential_drawbacks}"
            ) | client | parser
    )

    res = await research_aggregator.ainvoke({"prompt": base_prompt})
    print(str(res))


if __name__ == "__main__":
    asyncio.run(main())
