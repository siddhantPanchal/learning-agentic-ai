import json
import os
from typing import Literal, Optional

import requests


# from pydantic import BaseModel


# class Question(BaseModel):
#     pass
#
#
# class Choice(BaseModel, Question):
#     instructions: str
#     criteria: dict[str, str]
#
#
# class Score(BaseModel, Question):
#     instructions: str
#     criteria: dict[str, str]
#
#
# class Noul(BaseModel, Question):
#     instructions: str
#
#
# class SystemOneRequest(BaseModel):
#     state: str
#     questions: dict[str, Question]


class SystemOneModel:
    def __init__(self, model: str, model_provider: Literal["laya", "typesafe"], base_url: Optional[str] = None):
        self.model = model
        self.base_url = base_url or "https://api.typesafe.ai/v1/systemone" if model_provider == "typesafe" else "http://localhost:12434/engines/llama.cpp/v1/systemone"
        self.model_provider = model_provider

    def invoke(self, request: dict):
        api_key = os.environ.get(f"{self.model_provider.upper()}_API_KEY")
        state = request.get("state")
        questions = request.get("questions")

        # Build a flexible payload layout
        payload = {
            "state": state,
            "questions": questions
        }
        if self.model:
            payload["model"] = self.model
        print(payload)

        res = requests.post(
            url=self.base_url,
            json=json.dumps(payload),
            headers={"Content-Type": "application/json", "authorization": f"Bearer {api_key}"}
        )
        # res.raise_for_status()
        print(res.content)
        # print(res.json())

        # try:
        #     res = requests.post(
        #         url=self.base_url,
        #         data=payload,
        #         headers={"Content-Type": "application/json", "authorization": f"Bearer {api_key}"}
        #     )
        #     res.raise_for_status()
        #     print(res)
        #     print(res.json())
        # except requests.exceptions.RequestException as e:
        #     # Handle fallback logic if your 404/network drops
        #     return {"error": f"Failed connecting to server: {str(e)}"}
