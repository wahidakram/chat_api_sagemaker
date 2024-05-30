import boto3
from langchain_community.llms import SagemakerEndpoint
from config import config
from app.rag.content_handler import content_handler

roleARN = "arn:aws:iam::851725439453:role/SAGEMAKER-FULL"
sts_client = boto3.client("sts")
response = sts_client.assume_role(
    RoleArn=roleARN, RoleSessionName="wahid"
)

client = boto3.client(
    "sagemaker-runtime",
    region_name="eu-west-2",
    aws_access_key_id=response["Credentials"]["AccessKeyId"],
    aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
    aws_session_token=response["Credentials"]["SessionToken"],
)

endpoint_name = "pixelpai-dev-meta-textgeneration-l-20240520-091809"


def load_llm():
    llm = SagemakerEndpoint(
        endpoint_name=endpoint_name,
        client=client,
        # model_kwargs={
        #     "max_new_tokens": 200,
        #     "top_p": 0.8,
        #     "temperature": 0.8,
        #     "repetition_penalty": 1.0,
        # },
        model_kwargs={
            "max_new_tokens": 256,
            "top_p": 0.9,
            "temperature": 0.6,
            "stop": "<|eot_id|>",
            "repetition_penalty": 1.0,
        },
        content_handler=content_handler,
        endpoint_kwargs={"InferenceComponentName": 'meta-textgeneration-llama-3-8b-instruct-20240520-091811'},
    )
    return llm
