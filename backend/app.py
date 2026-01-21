from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from settings import TIPOS_PERMITIDOS, STATUS_PERMITIDOS

app = Flask(__name__)
CORS(app)

DATA_FILE = "items.json"


# ---------- Persistência ----------
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


# ---------- Validação ----------
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
@app.route("/items", methods=["GET"])
def get_items():
    items = load_items()

    tipo = request.args.get("tipo")
    status = request.args.get("status")
    search = request.args.get("search")

    if tipo:
        items = [i for i in items if i["tipo"] == tipo]
    if status:
        items = [i for i in items if i["status"] == status]
    if search:
        items = [i for i in items if search.lower() in i["titulo"].lower()]

    return jsonify(items), 200


@app.route("/items", methods=["POST"])
def create_item():
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


@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.json
    error = validate_item(data)
    if error:
        return jsonify({"error": error}), 400

    items = load_items()
    for item in items:
        if item["id"] == item_id:
            item.update({
                "titulo": data["titulo"],
                "tipo": data["tipo"],
                "status": data["status"],
                "descricao": data.get("descricao", ""),
                "valor": data.get("valor", 0)
            })
            save_items(items)
            return jsonify(item), 200

    return jsonify({"error": "Item não encontrado"}), 404


@app.route("/items/<int:item_id>/status", methods=["PATCH"])
def update_status(item_id):
    data = request.json
    if data.get("status") not in STATUS_PERMITIDOS:
        return jsonify({"error": "status inválido"}), 400

    items = load_items()
    for item in items:
        if item["id"] == item_id:
            item["status"] = data["status"]
            save_items(items)
            return jsonify(item), 200

    return jsonify({"error": "Item não encontrado"}), 404


@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    items = load_items()
    items = [i for i in items if i["id"] != item_id]
    save_items(items)
    return jsonify({"message": "Item removido"}), 200


if __name__ == "__main__":
    app.run(debug=True)
