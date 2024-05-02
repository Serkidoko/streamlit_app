from elasticsearch import  Elasticsearch
from loguru import logger
import sentence_transformers
from pyvi import ViTokenizer
import pandas as pd
from tqdm import tqdm
from elasticsearch.helpers import bulk
import json
def LLM_SMALL():
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
        config = json.load("/home/doducanh/Downloads/data/code_up/config_LLM_SMALL.json")

    create_index(
        client=client,
        index=INDEX_NAME,
        settings=config["es"]["settings"],
        mappings=config["es"]["mappings"]
    )

    def embeddings(text):
        segment = ViTokenizer.tokenize(text)
        embed = embedding_huggingface.encode(segment)
        return embed

    def create_es_document(index_name, question, answer, embeddings):
        """Create the elastic search document."""
        return {
            "_op_type": "index",
            "_index": index_name,
            "question": question,
            "answer": answer,
            "text_vector": embeddings.tolist(),
        }
        

    df = pd()
    df_section = df[["Câu hỏi", "Trả lời"]]
    df_section = df_section.dropna()
    data = []
    logger.info("starting push document")
    for item in tqdm(df_section.values):
        embed = embeddings(text=item[0])
        data.append(create_es_document(
            index_name=INDEX_NAME,
            question=item[0],
            answer=item[1],
            embeddings=embed
        ))
    bulk(client, data)
    logger.info("done")
LLM_SMALL()