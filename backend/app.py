from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from settings import TIPOS_PERMITIDOS, STATUS_PERMITIDOS

app = Flask(__name__)
CORS(app)  # libera CORS para frontend separado

DATA_FILE = "items.json"

# ---------- Funções Auxiliares ----------

def load_items():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_items(items):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

def next_id(items):
    if not items:
        return 1
    return max(item["id"] for item in items) + 1

def validate_item(data, partial=False):
    if not partial:
        if "titulo" not in data or len(data["titulo"].strip()) < 3:
            return "titulo é obrigatório e deve ter no mínimo 3 caracteres"
        if data.get("tipo") not in TIPOS_PERMITIDOS:
            return f"tipo inválido. Valores permitidos: {TIPOS_PERMITIDOS}"
        if data.get("status") not in STATUS_PERMITIDOS:
            return f"status inválido. Valores permitidos: {STATUS_PERMITIDOS}"
    if "valor" in data and data["valor"] < 0:
        return "valor não pode ser negativo"
    return None

# ---------- Rotas ----------

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API de Mini-Sistema de Registros rodando 🚀"})

@app.route("/items", methods=["GET", "POST"])
def items():
    if request.method == "GET":
        items = load_items()
        return jsonify(items)
    
    # POST
    data = request.json
    error = validate_item(data)
    if error:
        return jsonify({"error": error}), 400
    items = load_items()
    item = {
        "id": next_id(items),
        "titulo": data["titulo"],
        "tipo": data["tipo"],
        "status": data["status"],
        "descricao": data.get("descricao", ""),
        "valor": data.get("valor", 0)
    }
    items.append(item)
    save_items(items)
    return jsonify(item), 201

if __name__ == "__main__":
    app.run(debug=True)
