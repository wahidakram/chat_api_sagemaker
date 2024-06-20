import json
import os
import uuid

from flask import Blueprint, jsonify
from flask_restx import Api, Resource, fields, reqparse

from app.rag.redis_client import redis_client
from app.rag.loal_llm import load_llm
from langchain.chains.retrieval_qa.base import RetrievalQA

from app.rag.models import PDFFile
from app.rag.parser import question_parser, multiple_files_upload_parser, task_id_parser
from app.rag.vector_db import load_vector_store
from app.rag.prompt import PROMPT
from app.rag.tasks import process_pdf, queue, delete

from config import config

bp = Blueprint('api', __name__, url_prefix='/api')

api = Api(
    bp,
    version="1.0",
    title="Chat REST API",
    description="RAG",
)

ns = api.namespace("v1", description="RAG")
api.add_namespace(ns)


@ns.route("/chat")
class Chat(Resource):
    @ns.expect(question_parser)
    @ns.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
            description="Chat with the model", )
    def post(self):
        arg = question_parser.parse_args()
        vector_store = load_vector_store()
        chain = RetrievalQA.from_chain_type(
            llm=load_llm(),
            chain_type="stuff",
            retriever=vector_store.as_retriever(),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        result = chain.invoke({"query": arg.question})
        source_documents = []
        for doc in result["source_documents"]:
            source_documents.append({"source": doc.metadata["source"], "page": doc.metadata["page"]})
        return {
            "question": arg.question,
            "result": result["result"],
            "source_documents": source_documents
        }


@ns.route("/upload-files/")
class UploadFiles(Resource):
    """
    Upload multiple files
    """

    @ns.expect(multiple_files_upload_parser)
    @ns.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
            description="Upload multiple files for embedding and processing")
    def post(self):
        pdf_list = []
        try:
            task_id = str(uuid.uuid4())
            args = multiple_files_upload_parser.parse_args()
            files = args.files
            for file in files:
                if file.content_type != "application/pdf":
                    return {"message": "Only pdf and html files are supported"}
                file.save(f'pdfs/{file.filename}')
                pdf_list.append(f'{file.filename}')
            pdf_data = PDFFile(task_id=task_id, pdf_list=pdf_list)
            pdfs_json = json.dumps(pdf_data.__dict__)
            redis_client.set(task_id, pdfs_json)
            print(f"PDF file uploaded and split")
            queue.enqueue(process_pdf, task_id, pdf_data)
            return {
                "task_id": task_id,
                "pdf_list": pdf_list,
                "status": "processing"
            }
        except Exception as e:
            return {"error": str(e)}


@ns.route("/status")
class Status(Resource):
    @ns.expect(task_id_parser)
    @ns.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
            description="Get the status of the task")
    def get(self):
        args = task_id_parser.parse_args()
        task_id = args.get('task_id')
        status = redis_client.get(task_id)
        if status:
            return json.loads(status)
        else:
            return {"message": "Item ID Not Found"}


delete_file_model = ns.model('File', {
    'files_name': fields.List(fields.String, required=True),
})


@ns.route("/delete")
class Delete(Resource):
    @ns.expect(delete_file_model)
    @ns.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
            description="Delete files from the embedding")
    def delete(self, **kwargs):
        args = ns.payload
        files = args.get('files_name')
        print(f"Deleting files {files}")
        queue.enqueue(delete, files)
        return jsonify({f"message": f"Deleting files {files}"})