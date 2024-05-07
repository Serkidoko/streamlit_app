from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from transformers import AutoTokenizer
from elasticsearch import  Elasticsearch
from loguru import logger
import sentence_transformers
import os
from elasticsearch.helpers import bulk
import json
import glob
import uuid
import pandas as pd
from tritonclient.utils import *
import tritonclient.grpc as grpc_client
#----------------------------------------------------------------

CONFIG_FILE = "/home/doducanh/Downloads/data/code_up/config_LLM_SMALL.json"

#----------------------------------------------------------------

model_tokenizer = AutoTokenizer
# folder_dataraw = "/home/ninh/phenikaax/virtual_assistant/Trien_khai/chatbot_tuyen_sinh/upload_data_to_server/data_raw"

client = Elasticsearch(
    hosts="https://10.20.76.19:9200", 
    basic_auth=("data_chatbot","dataphenikaa"),
    verify_certs=False)

# embedding_huggingface = sentence_transformers.SentenceTransformer(
#     model_name_or_path="BAAI/bge-m3"
# )

#----------------------------------------------------------------
# def embeddings(text):
#     # segment = ViTokenizer.tokenize(text)
#     embed = embedding_huggingface.encode(text)
#     return embed
def get_triton_client():
    client = grpc_client.InferenceServerClient("10.20.76.19:8002")
    return client
def embeddings(text: str = None):
    """get embedding text"""
    input_data = np.frombuffer(bytes(text, "utf-8"), dtype=np.uint8)
    inputs = [grpc_client.InferInput("text_input", input_data.shape, "UINT8")]
    inputs[0].set_data_from_numpy(input_data)
    output = [grpc_client.InferRequestedOutput("embedding_output")]
    client = get_triton_client()
    try:
        response = client.infer(
            model_name="embedding_triton",
            inputs=inputs,
            outputs=output,
            model_version="1",
            request_id="chatbot"
        )
    except Exception as e:
        logger.error(e)
        logger.error("Failed to get embeddings")
    if response:
        embedded = response.as_numpy("embedding_output")
        return embedded.tolist()
    else:
        return None

def create_index(client, index, settings, mappings):
    if not client.indices.exists(index=index).body:
        client.indices.create(
            index=index, settings=settings, mappings=mappings,
        )
        logger.info(f"{index} created")


def create_es_document(index_name, document, url, embeddings,id_doc,file_name):
    """Create the elastic search document."""
    return {
        "_op_type": "index",
        "_index": index_name,
        "text": document,
        "url": url,
        "id_doc":id_doc,
        "file_name":file_name,
        "text_vector": embeddings
    }
#----------------------------------------------------------------
with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)
#----------------------------------------------------------------
name_directories = []
name_phongban = name_directories

for name_dir in name_directories:
    df = pd.read_excel(sheet_name=name_dir)
    path_dir = os.path.join(name_dir)
    docx_files = glob.glob(os.path.join(path_dir, '*.docx'))
    # doc_files = glob.glob(os.path.join(path_dir, '*.doc'))
    # docx_files = docx_files + doc_files
    INDEX_NAME = f"llm-small-{name_dir}-2024.04.24".lower()
    if docx_files != []:
        create_index(
            client=client,
            index=INDEX_NAME,
            settings=config["es"]["settings"],
            mappings=config["es"]["mappings"]
        )
        data_es = []
        for file_doc in docx_files:

            try:
                file_name = os.path.basename(file_doc)
                loader = UnstructuredWordDocumentLoader(file_doc)
                documents = loader.load()
                text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(chunk_size=500, chunk_overlap=0, tokenizer = model_tokenizer)
                docs = text_splitter.split_documents(documents)
                id_doc = str(uuid.uuid4())
                for id in range(len(docs)):
                    id_doc_stt = f"{id_doc}_{id}"
                    text = docs[id].page_content.lower()
                    if len(text) > 200:
                        embed = embeddings(text=f"{file_name}: " + text)
                    else:
                        embed = embeddings(text=text)
                    # embed = embeddings(text=text)
                    url = df.loc[df['Tên file'] == file_name, 'Link'].values
                    data_es.append(create_es_document(
                        index_name=INDEX_NAME,
                        document=text,
                        url=url,
                        file_name=file_name,
                        embeddings=embed,
                        id_doc=id_doc_stt
                    ))
            except:
                print(file_doc)
        bulk(client, data_es)
logger.info("done !!!")