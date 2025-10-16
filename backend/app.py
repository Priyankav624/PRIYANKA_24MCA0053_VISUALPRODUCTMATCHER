from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from sentence_transformers import SentenceTransformer, util
import io, os, json, torch, pickle, requests, threading

app = Flask(__name__)
CORS(app)

# Global variables
model = None
products = []
product_embeddings = None
CACHE_PATH = "embeddings_cache.pkl"
MODEL_NAME = "clip-ViT-L-14"

@app.route("/")
def home():
    return jsonify({"message": "Visual Product Matcher API Running"})

@app.route("/api/search", methods=["POST"])
def search_similar():
    global model, products, product_embeddings
    if model is None or product_embeddings is None:
        return jsonify({"error": "Model is still loading, please wait 1–2 minutes."}), 503

    try:
        if "file" in request.files:
            img_bytes = request.files["file"].read()
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        elif request.is_json and "url" in request.json:
            image = Image.open(requests.get(request.json["url"], stream=True).raw).convert("RGB")
        else:
            return jsonify({"error": "No image provided"}), 400

        query_embedding = model.encode(image, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, product_embeddings)[0]
        top_results = torch.topk(scores, k=10)

        results = []
        for idx, score in zip(top_results.indices, top_results.values):
            p = products[idx]
            p["similarity"] = round(float(score), 4)
            results.append(p)

        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def load_resources():
    global model, products, product_embeddings
    try:
        print("⏳ Loading model and products...")
        model = SentenceTransformer(MODEL_NAME)

        with open("products.json", "r") as f:
            products = json.load(f)

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
        print("✅ Model & embeddings loaded successfully.")
    except Exception as e:
        print("❌ Resource loading error:", e)

def get_image_embedding(image_path_or_url):
    global model
    try:
        if image_path_or_url.startswith("http"):
            image = Image.open(requests.get(image_path_or_url, stream=True).raw).convert("RGB")
        else:
            image = Image.open(image_path_or_url).convert("RGB")
        return model.encode(image, convert_to_tensor=True)
    except Exception as e:
        print("Embedding error:", e)
        return None

if __name__ == "__main__":
    # Start model loading in background
    threading.Thread(target=load_resources).start()
    port = int(os.environ.get("PORT", 5000))
    print(f"🔥 Starting Flask on port {port} ...")
    app.run(host="0.0.0.0", port=port)
