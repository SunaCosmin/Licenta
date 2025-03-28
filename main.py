import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import matplotlib.pyplot as plt
from embedding_extractor import EmbeddingExtractor

model_name = "microsoft/markuplm-base"

extractor = EmbeddingExtractor(model_name=model_name,
                               pooling="max",
                               workers=80,
                               use_text=False)

my_embeddings=extractor.extract_embeddings()
all_embeddings = np.array(my_embeddings)

pca = PCA(n_components=2)
embeddings_2d = pca.fit_transform(all_embeddings)

def apply_clustering(algorithm, embeddings):

    clusters = algorithm.fit_predict(embeddings)

    if len(np.unique(clusters)) > 1:
        silhouette = silhouette_score(embeddings, clusters)
        print(f"Silhouette Score: {silhouette:.3f}")

    calinski = calinski_harabasz_score(embeddings, clusters)
    print(f"Calinski-Harabasz Score: {calinski:.3f}")

    plt.figure(figsize=(12, 8))

    for i, (x, y) in enumerate(embeddings_2d):
        plt.scatter(x, y, c=[plt.cm.viridis(clusters[i] / float(max(clusters) + 1))],
                    marker='o', alpha=0.7, s=100)

    plt.grid(True, alpha=0.3)
    plt.title(f"The number of unique clusters is {len(np.unique(clusters))} with no text")
    plt.show()

    return clusters

dbscan = DBSCAN(eps=0.3, min_samples=5)
dbscan_clusters = apply_clustering(dbscan, all_embeddings)

