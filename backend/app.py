from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer, util
from PIL import Image
from flask_cors import CORS
import io, os, json, torch, pickle, requests

app = Flask(__name__)
CORS(app)  # Allow frontend access (React app)

# ----------------------------
# Model and data setup
# ----------------------------
model = SentenceTransformer("clip-ViT-L-14")

# Load products data
with open("products.json", "r") as f:
    products = json.load(f)

CACHE_PATH = "embeddings_cache.pkl"  # Cache for precomputed embeddings

# ----------------------------
# Helper: Generate image embedding
# ----------------------------
def get_image_embedding(image_path_or_url):
    """
    Returns a tensor embedding for a given image (local path or URL).
    Returns None if the image cannot be processed.
    """
    try:
        if image_path_or_url.startswith("http"):
            image = Image.open(requests.get(image_path_or_url, stream=True).raw).convert("RGB")
        else:
            image = Image.open(image_path_or_url).convert("RGB")
        return model.encode(image, convert_to_tensor=True)
    except Exception as e:
        print("Embedding error:", e)
        return None

# ----------------------------
# Load or compute embeddings
# ----------------------------
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, "rb") as f:
        product_embeddings = pickle.load(f)
else:
    product_embeddings = []
    for p in products:
        emb = get_image_embedding(p["image"])
        if emb is not None:
            product_embeddings.append(emb)
    with open(CACHE_PATH, "wb") as f:
        pickle.dump(product_embeddings, f)

product_embeddings = torch.stack(product_embeddings)

# ----------------------------
# API route: Search similar images
# ----------------------------
@app.route("/api/search", methods=["POST"])
def search_similar():
    """
    Accepts image (file or URL), computes embedding,
    compares with stored product embeddings, and returns top matches.
    """
    try:
        # Accept either uploaded file or image URL
        if "file" in request.files:
            img_bytes = request.files["file"].read()
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        elif request.is_json and "url" in request.json:
            image = Image.open(requests.get(request.json["url"], stream=True).raw).convert("RGB")
        else:
            return jsonify({"error": "No image provided"}), 400

        # Compute similarity scores
        query_embedding = model.encode(image, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, product_embeddings)[0]
        top_results = torch.topk(scores, k=10)

        # Collect top results
        results = []
        for idx, score in zip(top_results.indices, top_results.values):
            p = products[idx]
            p["similarity"] = round(float(score), 4)
            results.append(p)

        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------
# Health check endpoint
# ----------------------------
@app.route("/")
def home():
    return jsonify({"message": "Visual Product Matcher API Running"})

# ----------------------------
# Application entry point
# ----------------------------
if __name__ == "__main__":
    print("Flask server starting on port", os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
