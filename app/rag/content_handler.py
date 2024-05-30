from langchain_community.llms.sagemaker_endpoint import LLMContentHandler
import json
from typing import Dict


class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
        input_str = json.dumps({"inputs": prompt, "parameters": model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        print(type(output))
        response_json = json.loads(output.read().decode("utf-8"))
        # pprint(response_json["generated_text"])
        return response_json["generated_text"]


content_handler = ContentHandler()
