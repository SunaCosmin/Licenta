import torch
from transformers import MarkupLMProcessor, MarkupLMModel,MarkupLMFeatureExtractor
import numpy as np


processor = MarkupLMProcessor.from_pretrained("microsoft/markuplm-base")
model = MarkupLMModel.from_pretrained("microsoft/markuplm-base")
feature_extractor=MarkupLMFeatureExtractor()


# Example 1: Simple login form HTML
html_login = """
<!DOCTYPE html>
<html>
<head>
    <title>Login Page</title>
</head>
<body>
    <div class="login-container">
        <h2>Login</h2>
        <form action="/login" method="post">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Log In</button>
        </form>
        <div class="links">
            <a href="/forgot-password">Forgot Password?</a>
            <a href="/signup">Create Account</a>
        </div>
    </div>
</body>
</html>
"""

# Example 2: Complex data table visualization HTML
html_data_viz = """
<!DOCTYPE html>
<html>
<head>
    <title>Climate Data Visualization</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <header>
        <h1>Global Temperature Analysis Dashboard</h1>
        <div class="time-controls">
            <button data-range="1y">1 Year</button>
            <button data-range="5y">5 Years</button>
            <button data-range="10y">10 Years</button>
            <button data-range="max">All Data</button>
        </div>
    </header>
    <main>
        <section class="chart-container">
            <svg id="temperature-chart" width="800" height="400">
                <g class="x-axis"></g>
                <g class="y-axis"></g>
                <g class="plot-area">
                    <path class="line-path" d="M0,120 L100,145 L200,180 L300,210 L400,250 L500,230 L600,270 L700,290"></path>
                    <circle class="data-point" cx="0" cy="120" r="4"></circle>
                    <circle class="data-point" cx="100" cy="145" r="4"></circle>
                    <circle class="data-point" cx="200" cy="180" r="4"></circle>
                    <circle class="data-point" cx="300" cy="210" r="4"></circle>
                    <circle class="data-point" cx="400" cy="250" r="4"></circle>
                    <circle class="data-point" cx="500" cy="230" r="4"></circle>
                    <circle class="data-point" cx="600" cy="270" r="4"></circle>
                    <circle class="data-point" cx="700" cy="290" r="4"></circle>
                </g>
            </svg>
            <div class="chart-legend">
                <div class="legend-item">
                    <span class="color-box" style="background-color: #ff6347;"></span>
                    <span class="legend-text">Global Average</span>
                </div>
                <div class="legend-item">
                    <span class="color-box" style="background-color: #4682b4;"></span>
                    <span class="legend-text">Northern Hemisphere</span>
                </div>
                <div class="legend-item">
                    <span class="color-box" style="background-color: #32cd32;"></span>
                    <span class="legend-text">Southern Hemisphere</span>
                </div>
            </div>
        </section>
        <section class="data-table">
            <table>
                <thead>
                    <tr>
                        <th>Year</th>
                        <th>Global (°C)</th>
                        <th>N. Hemisphere (°C)</th>
                        <th>S. Hemisphere (°C)</th>
                        <th>Anomaly</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>2020</td><td>14.9</td><td>15.7</td><td>14.1</td><td>+1.2</td></tr>
                    <tr><td>2021</td><td>14.8</td><td>15.5</td><td>14.0</td><td>+1.1</td></tr>
                    <tr><td>2022</td><td>15.0</td><td>15.8</td><td>14.2</td><td>+1.3</td></tr>
                    <tr><td>2023</td><td>15.2</td><td>16.1</td><td>14.3</td><td>+1.5</td></tr>
                    <tr><td>2024</td><td>15.4</td><td>16.3</td><td>14.5</td><td>+1.7</td></tr>
                </tbody>
            </table>
        </section>
    </main>
    <aside class="analysis-panel">
        <h3>Key Findings</h3>
        <ul>
            <li>Global temperatures have risen by an average of 0.12°C per decade</li>
            <li>Northern hemisphere warming is 40% faster than southern hemisphere</li>
            <li>Ocean temperature anomalies show increasing variance</li>
            <li>Arctic regions show 3x the global average increase</li>
        </ul>
        <div class="download-options">
            <button data-format="csv">Download CSV</button>
            <button data-format="json">Download JSON</button>
            <button data-format="pdf">Download Report</button>
        </div>
    </aside>
</body>
</html>
"""



features_page1=feature_extractor(html_login)
features_page2=feature_extractor(html_data_viz)


encoding_1 = processor(html_login,return_tensors="pt")
encoding_2 = processor(html_data_viz,return_tensors="pt")


with torch.no_grad():
    outputs_1 = model(**encoding_1)
    outputs_2 = model(**encoding_2)

embeddings_1 = outputs_1.last_hidden_state
embeddings_2 = outputs_2.last_hidden_state

embedding_vectors_1 = embeddings_1.squeeze(0).tolist()
embedding_vectors_2 = embeddings_2.squeeze(0).tolist()

array1=np.array(embedding_vectors_1)

mean_array1=np.mean(array1,axis=0)

array2=np.array(embedding_vectors_2)

mean_array2=np.mean(array2,axis=0)


cosine_similarity = np.dot(mean_array1, mean_array2) / (np.linalg.norm(mean_array1) * np.linalg.norm(mean_array2))

print("Cosine similarity:",cosine_similarity)