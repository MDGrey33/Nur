# Import necessary libraries
from database.page_manager import get_all_page_data_from_db
from sklearn.cluster import KMeans
import numpy as np
import json
import plotly.graph_objects as go  # Import Plotly Graph Objects for 3D plotting
from umap import UMAP  # Ensure umap-learn is installed


def visualize_page_clusters_3d(n_clusters=10):
    print("Starting 3D visualization process...")

    # Step 1: Retrieve all page data, including embeddings, titles, and space keys
    page_ids, all_documents, embeddings_json = get_all_page_data_from_db()
    print(f"Retrieved {len(embeddings_json)} embeddings from the database.")

    if not embeddings_json:
        print("No embeddings found. Exiting visualization process.")
        return

    embeddings = [json.loads(embed) for embed in embeddings_json if embed]
    print(f"Successfully deserialized {len(embeddings)} embeddings.")

    if not embeddings:
        print("No valid embeddings after deserialization. Exiting visualization process.")
        return

    # Extract titles and space keys from all_documents
    titles = [doc.split(",")[2].split(":")[1].strip() for doc in all_documents]
    space_keys = [doc.split(",")[1].split(":")[1].strip() for doc in all_documents]

    # Convert embeddings to a NumPy array for processing
    embeddings_array = np.array(embeddings)
    print(f"Converted embeddings to NumPy array with shape {embeddings_array.shape}.")

    # Step 2: Use UMAP for dimensionality reduction to 3 components for 3D visualization
    umap = UMAP(n_components=3)
    reduced_embeddings = umap.fit_transform(embeddings_array)
    print("Dimensionality reduction completed using UMAP.")

    # Step 2.5: Apply KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters)
    cluster_labels = kmeans.fit_predict(reduced_embeddings)
    print(f"KMeans clustering completed with {n_clusters} clusters.")

    # Prepare hover text with titles and space keys
    hover_texts = [f"{title}<br>Space Key: {key}" for title, key in zip(titles, space_keys)]

    # Step 3: Visualization with cluster colors and hover texts using Plotly 3D scatter plot
    fig = go.Figure(data=[go.Scatter3d(
        x=reduced_embeddings[:, 0],
        y=reduced_embeddings[:, 1],
        z=reduced_embeddings[:, 2],
        mode='markers',
        marker=dict(
            size=5,  # Set a default size for all dots
            color=cluster_labels,  # Use cluster labels for colors
            colorscale='Viridis',  # Color scale for clusters
            opacity=0.8,
            colorbar=dict(title='Cluster Label'),
        ),
        text=hover_texts,  # Use hover texts for custom hover information
    )])

    fig.update_layout(title='3D Page Embeddings Clusters Visualization')
    fig.show()

    print("3D Clustered visualization displayed.")


if __name__ == '__main__':
    visualize_page_clusters_3d()
