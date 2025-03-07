import torch
from transformers import MarkupLMProcessor, MarkupLMModel, MarkupLMFeatureExtractor
import Tree_Generator


processor = MarkupLMProcessor.from_pretrained("microsoft/markuplm-base")
model = MarkupLMModel.from_pretrained("microsoft/markuplm-base")
feature_extractor = MarkupLMFeatureExtractor()


with open("html_files/fake.html", "r", encoding="utf-8") as f:
    html1 = f.read()

with open("html_files/legit.html", "r", encoding="utf-8") as f:
    html2 = f.read()

with open("html_files/data_viz.html", "r", encoding="utf-8") as f:
    html_data_viz = f.read()


features = feature_extractor(html_data_viz)
xpaths = features.xpaths[0]
nodes = features.nodes[0]

my_dict={}

for xpath, node in zip(xpaths, nodes):
    my_dict[xpath] = node

print(my_dict)


tree = Tree_Generator.build_tree(xpaths, nodes)


encoding = processor(html_data_viz, return_tensors="pt")


with torch.no_grad():
    outputs_1 = model(**encoding)

embeddings_1 = outputs_1.last_hidden_state


tokens = processor.tokenizer.convert_ids_to_tokens(encoding["input_ids"].squeeze().tolist())


embedding_vectors_1 = embeddings_1.squeeze(0).tolist()


#for token, embedding in zip(tokens, embedding_vectors_1):
#    print(f"Token: {token} -> Embedding: {embedding}")
