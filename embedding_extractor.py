from pathlib import Path
from transformers import MarkupLMProcessor,AutoModel
import numpy as np
from os import path
import threading

class EmbeddingExtractor:

    def __init__(self, model_name, pooling,workers,use_text=True):
        self.model_name = model_name
        self.pooling = pooling
        self.use_text = use_text
        self.processor = MarkupLMProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.embedding_dict = {}
        self.workers = workers

    def get_html_encoding(self, html, pooling="max", use_text=True):
        model_input = self.processor(html, return_tensors="pt", truncation=True, max_length=512)

        if use_text:
            xpath_embeddings = self.model.embeddings(
                input_ids=model_input['input_ids'],
                xpath_tags_seq=model_input['xpath_tags_seq'],
                xpath_subs_seq=model_input['xpath_subs_seq'],
                token_type_ids=model_input['token_type_ids']
            ).detach().numpy()[0]
        else:
            xpath_embeddings = self.model.embeddings.xpath_embeddings(
                model_input['xpath_tags_seq'],
                model_input['xpath_subs_seq']
            ).detach().numpy()[0]

        embeddings = xpath_embeddings

        if pooling == "avg":
            return np.mean(embeddings, axis=0)
        elif pooling == "max":
            return np.max(embeddings, axis=0)
        else:
            raise ValueError("Unknown pooling strategy")

    def partition_list(self, lst, num_chunks):
        if(num_chunks > len(lst)):
            raise ValueError(f"To many workers added the maximum number is {len(list)}")

        avg = len(lst) // num_chunks
        remainder = len(lst) % num_chunks
        chunks = []
        start = 0

        for i in range(num_chunks):
            end = start + avg + (1 if i < remainder else 0)
            chunks.append(lst[start:end])
            start = end

        return chunks

    def get_html_information(self, path):
        directory = Path(path)
        html_codes = []
        filenames = []
        for filepath in directory.rglob("*.html"):
            if filepath.is_file():
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_codes.append(f.read())
                    filenames.append(filepath.parent.name)
        return html_codes, filenames

    def worker(self, html_codes, worker_id):
        embeddings = []
        for html in html_codes:
            embeddings.append(self.get_html_encoding(html))
        self.embedding_dict[worker_id] = embeddings

    def extract_embeddings(self):
        html_codes, filenames = self.get_html_information("data")
        partial_embeddings = self.partition_list(html_codes, self.workers)

        threads = []
        for worker_id, embeddings in enumerate(partial_embeddings):
            thread = threading.Thread(target=self.worker, args=(embeddings, worker_id))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        my_embeddings = []
        for embeddings in self.embedding_dict.values():
            for embedding in embeddings:
                my_embeddings.append(embedding)

        return my_embeddings



