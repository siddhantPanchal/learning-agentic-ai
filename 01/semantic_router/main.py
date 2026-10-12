from dotenv import load_dotenv

load_dotenv()
from langchain_core.runnables import RunnableLambda, RunnableBranch

from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# from langchain_typesafe import TypeSafeClassifier, Choice

from langchain.chat_models import init_chat_model


class SelectedModel(BaseModel):
    model_name: str = Field(description="The name of the category. this can either coding or sql or general")


base_url = "http://localhost:12434/v1"

classifier_model = init_chat_model(model="gemma4:E2B", model_provider="openai", base_url=base_url)
general_model = init_chat_model(model="gemma3:270M-F16", model_provider="openai", base_url=base_url)
sql_model = init_chat_model(model="qwen3:0.6B-F16", model_provider="openai", base_url=base_url)
coding_model = init_chat_model(model="gemma4:E2B", model_provider="openai", base_url=base_url)

parser = StrOutputParser()
pydantic_parser = PydanticOutputParser(pydantic_object=SelectedModel)


def main():
    # prompt: str = str(input("User > "))
    prompt = "what alter query does?"
    # print(pydantic_parser.get_format_instructions())

    router_branch = RunnableBranch(
        (
            lambda cat: str(cat) == "sql",
            ChatPromptTemplate.from_messages([
                (
                    "system",
                    "You are a precise SQL and database specialist. Do NOT greet the user. Do NOT explain your capabilities. Directly fulfill the user's technical request immediately."
                ),
                ("human", "{raw_prompt}")]
            ) | sql_model
        ), (
            lambda cat: str(cat) == "coding",
            ChatPromptTemplate.from_messages([
                (
                    "system",
                    "You are an expert software engineer. Do NOT output generic introductions, greetings, or lists of what you can do. Go straight to writing the code or answering the prompt provided in the human message."
                ),
                ("human", "{raw_prompt}")]
            ) | coding_model
        ),
        ChatPromptTemplate.from_messages([
            ("human", "{raw_prompt}")
        ]) | general_model
    ) | parser

    final_chain = (
            ChatPromptTemplate.from_template("""
                    Please categorize the provided prompt based on whether prompt is related to sql or coding or related any general prompt.
                    You can fallback to general category.
                    the prompt is `{raw_prompt}`.
                    {format_instructions} 
                    """, ) | classifier_model | pydantic_parser
            |
            RunnableLambda(lambda x: {"category": str(x.model_name).lower(), "raw_prompt": prompt}) |
            # Step C: Route the prompt layout using the calculated category
            RunnableLambda(lambda inputs: router_branch.invoke(
                {"raw_prompt": inputs["raw_prompt"]},
                config={"category": inputs["category"]}
            )) | parser
    )

    result = final_chain.invoke(
        {"raw_prompt": prompt, "format_instructions": pydantic_parser.get_format_instructions()})

    print(result)


if __name__ == '__main__':
    main()
