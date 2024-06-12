import json
import os
import pandas as pd
from rq import Queue
from app.rag.redis_client import redis_client
from app.rag.load_data import load_split_pdf_file, initialize_splitter
from app.rag.vector_db import update_vector_store, load_vector_store, save_vector_store


def process_pdf(pdf_id, pdf_data):
    pdf_data = redis_client.get(pdf_id)
    pdf_data = json.loads(pdf_data)
    for pdf in pdf_data["pdf_list"]:
        pdf_file = f"pdfs/{pdf}"
        if os.path.exists(pdf_file):
            print(f"Processing {pdf}")
        text_splitter = initialize_splitter(1000, 100)
        documents = load_split_pdf_file(pdf_file, text_splitter)
        print(f"Loaded {len(documents)} documents")
        update_vector_store(documents)
    with redis_client.pipeline() as pipe:
        pipe.multi()
        pdf_data["status"] = "done"
        pipe.set(pdf_id, json.dumps(pdf_data))
        pipe.execute()


def store_to_df(store):
    vector_dict = store.docstore._dict
    data_rows = []
    for k in vector_dict.keys():
        doc_name = vector_dict[k].metadata['source'].split('/')[-1]
        page_number = vector_dict[k].metadata['page'] + 1
        content = vector_dict[k].page_content
        data_rows.append({"chunk_id": k, "document": doc_name, "page": page_number, "content": content})
    vector_df = pd.DataFrame(data_rows)
    return vector_df


def delete(docs_name):
    try:
        print(f"{docs_name}")
        vector_store = load_vector_store()
        vector_df = store_to_df(vector_store)
        for doc in docs_name:
            chunk_list = vector_df.loc[vector_df['document'] == doc]['chunk_id'].tolist()
            print(f"Deleting chunks from {doc} from vector store {len(chunk_list)}")
            vector_store.delete(chunk_list)
            save_vector_store(vector_store)
    except Exception as e:
        return str(e)


queue = Queue(connection=redis_client.connect())
