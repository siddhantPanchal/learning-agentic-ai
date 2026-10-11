import asyncio
import datetime
import threading

from dotenv import load_dotenv, dotenv_values
from openai import OpenAI
from openai.types.responses import ParsedResponse
from pydantic import BaseModel

load_dotenv()

client = OpenAI(
    base_url=dotenv_values()["BASE_URL"],
)
model = dotenv_values()["MODEL"] or ""


class Information(BaseModel):
    customer: str
    amount: str
    currency: str
    product: str
    relative_date: str


async def extractAsync(input_text: str) -> str:
    print("Extracting information...")
    res: ParsedResponse = client.responses.parse(
        model=model, input=input_text,
        instructions="You are an AI algorithm to extract the details from given input text. user will provide the text and output as valid JSON",
        text_format=Information)
    print(f"Extracted information: {res.output_parsed}")
    return str(res.output_parsed)


def extract(input_text: str) -> str:
    print("Extracting information...")
    res: ParsedResponse = client.responses.parse(
        model=model, input=input_text,
        instructions="You are an AI algorithm to extract the details from given input text. user will provide the text and output as valid JSON",
        text_format=Information)
    print(f"Extracted information: {res.output_parsed}")
    return str(res.output_parsed)


async def classifyAsync(input_text: str) -> str:
    print("Classifying information...")
    res = client.responses.create(
        model=model,
        instructions="You are an classification expert in classifying the text based on its technical details. use score to classify the text.",
        input=input_text
    )
    print(f"Classified information... : {res.output_text}")
    return str(res.output_text)


def classify(input_text: str) -> str:
    print("Classifying information...")
    res = client.responses.create(
        model=model,
        instructions="You are an classification expert in classifying the text based on its technical details. use score to classify the text.",
        input=input_text
    )
    print(f"Classified information... : {res.output_text}")
    return str(res.output_text)


async def summarizeAsync(input_text: str) -> str:
    print("Summarizing information...")
    res = client.responses.create(
        model=model,
        instructions="You are an expert in summarizing the given text. you will summarize the text in 2-3 sentences",
        input=input_text
    )
    print(f"Summarized information... : {res.output_text}")
    return str(res.output_text)


def summarize(input_text: str) -> str:
    print("Summarizing information...")
    res = client.responses.create(
        model=model,
        instructions="You are an expert in summarizing the given text. you will summarize the text in 2-3 sentences",
        input=input_text
    )
    print(f"Summarized information... : {res.output_text}")
    return str(res.output_text)


async def main():
    summarizeText = """Music is the arrangement of sound to create some combination of form, harmony, melody, rhythm, or otherwise expressive content.[1][2][3] Music is generally agreed to be a cultural universal that is present in all human societies.[4] Definitions of music vary widely in substance and approach.[5] While scholars agree that music is defined by a small number of specific elements, there is no consensus as to what these necessary elements are.[6] Music is often characterized as a highly versatile medium for expressing human creativity.[7] Diverse activities are involved in the creation of music, and are often divided into categories of composition, improvisation, and performance.[8] Music may be performed using a wide variety of musical instruments, including the human voice. It can also be composed, sequenced, or otherwise produced to be indirectly played mechanically or electronically, such as via a music box, barrel organ, or digital audio workstation software on a computer.
     Music often plays a key role in social events and religious ceremonies. The techniques of making music are often transmitted as part of a cultural tradition. Music is played in public and private contexts, highlighted at events such as festivals and concerts for various different types of ensembles. Music is used in the production of other media, such as in soundtracks to films, TV shows, operas, and video games.
     Listening to music is a common means of entertainment. The culture surrounding music extends into areas of academic study, journalism, philosophy, psychology, and therapy. The music industry includes songwriters, performers, sound engineers, producers, tour organizers, distributors of instruments, accessories, and publishers of sheet music and recordings. Technology facilitating the recording and reproduction of music has historically included sheet music, microphones, phonographs, and tape machines, with playback of digital music being a common use for MP3 players, CD players, and smartphones."""

    start = datetime.datetime.now()
    print(f"Start Time : {start}")
    print(await extractAsync(input_text="John ordered an iPhone 15 yesterday for ₹72,000."))
    print(await classifyAsync(input_text="John ordered an iPhone 15 yesterday for ₹72,000."))
    print(await summarizeAsync(input_text=summarizeText))
    print(f"Finish Time : {datetime.datetime.now()} Total Time : {(datetime.datetime.now() - start).total_seconds()}")

    start = datetime.datetime.now()
    print(f"Start Time : {start}")
    t1 = threading.Thread(target=extract, args=("John ordered an iPhone 15 yesterday for ₹72,000.",))
    t1.start()
    t2 = threading.Thread(target=classify, args=("John ordered an iPhone 15 yesterday for ₹72,000.",))
    t2.start()
    t3 = threading.Thread(target=summarize, args=(summarizeText,))
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    print(f"Finish Time : {datetime.datetime.now()} Total Time : {(datetime.datetime.now() - start).total_seconds()}")


if __name__ == "__main__":
    asyncio.run(main())
