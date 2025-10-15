# Visual Product Matcher

### 🧠 Live Demo
[Click here to view the deployed app](https://your-deployment-url.example)

A mobile-responsive web app that finds visually similar products from a catalog of images.  
Upload an image (file or URL) and get ranked results with similarity scores and simple filters.

---

## 🧩 Tech Stack

**Backend:** Python Flask, sentence-transformers (CLIP clip-ViT-L-14)  
**Frontend:** React + Tailwind CSS (CDN or integrated build)  
**Storage:** Product metadata JSON + cached embeddings (pickle)

---

## 🚀 Features

- Image upload by file or image URL  
- Shows uploaded preview and top similar products (with similarity % & progress bar)  
- Client-side filter (minimum similarity slider)  
- Loading states and basic error handling  
- Responsive layout for mobile and desktop  

---

## 🧱 Run Locally (Backend)

```bash
cd backend
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Ensure products.json exists
#    under backend/static/product_images/
#    or provide remote URLs

# 4. Start backend
python app.py
````

---

## 💻 Run Locally (Frontend)

```bash
cd frontend
npm install
npm run dev
```

---

## 🔗 API Endpoints

### `POST /api/search`

**Accepts:**

* multipart form-data (`file`)
* or JSON `{ "url": "<image_url>" }`

**Returns:**

```json
{
  "results": [
    { "id": 1, "name": "Product A", "category": "Shoes", "image": "image_url", "similarity": 0.89 },
    ...
  ]
}
```

---

### `GET /`

**Returns:**

```json
{ "status": "Server running successfully." }
```

---
