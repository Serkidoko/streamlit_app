from elasticsearch import  Elasticsearch
from loguru import logger
import sentence_transformers
from pyvi import ViTokenizer
import os
from tqdm import tqdm
from elasticsearch.helpers import bulk
import json
def LLM_FULL():
    #----------------------------------------------------------------
    INDEX_NAME = ""
    URL = ""
    FILE_DIR = ""
    CONFIG_FILE = ""
    #----------------------------------------------------------------

    client = Elasticsearch(
        hosts="https://10.20.77.96:9200", 
        basic_auth=("data_chatbot","dataphenikaa"),
        verify_certs=False)

    embedding_huggingface = sentence_transformers.SentenceTransformer(
        model_name_or_path="BAAI/bge-m3"
    )
    def create_index(client, index, settings, mappings):
        if not client.indices.exists(index=index).body:
            client.indices.create(
                index=index, settings=settings, mappings=mappings,
            )
            logger.info(f"{index} created")


    with open(CONFIG_FILE) as _:
        config = json.load("/home/doducanh/Downloads/data/code_up/config_LLM_FULL.json")

    create_index(
        client=client,
        index=INDEX_NAME,
        settings=config["es"]["settings"],
        mappings=config["es"]["mappings"]
    )

    def create_es_document(index_name, document, url, embeddings):
        """Create the elastic search document."""
        return {
            "_op_type": "index",
            "_index": index_name,
            "text": document,
            "url": url
        }
        
    logger.info("Starting push document")
    data = []
    for text in tqdm(os.listdir(FILE_DIR), desc="dirs"):
        text_path = os.path.join(FILE_DIR, text)
        with open(text_path, "r+") as text_file:
            text = text_file.read()
        data.append(create_es_document(
            index_name=INDEX_NAME,
            document=text,
            url=URL
        ))
        

    bulk(client, data)
    logger.info("done !!!")
LLM_FULL()