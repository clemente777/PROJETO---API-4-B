from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

NOME_ARQUIVO = 'pizzas.json'

def ler_dados():
    if not os.path.exists(NOME_ARQUIVO):
        return []
    with open(NOME_ARQUIVO, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_dados(pizzas):
    with open(NOME_ARQUIVO, 'w', encoding='utf-8') as f:
        json.dump(pizzas, f, indent=4, ensure_ascii=False)

# Rota para carregar o Front-end
@app.route('/')
def home():
    return render_template('index.html')

# Listar pizzas
@app.route('/pizzas', methods=['GET'])
def obter_sabores():
    return jsonify(ler_dados())

# Adicionar pizza com ID Automático
@app.route('/pizzas', methods=['POST'])
def adicionar_pizza():
    pizzas = ler_dados()
    nova_pizza = request.get_json()

    # --- LÓGICA AUTO-INCREMENTO ---
    if len(pizzas) > 0:
        # Pega o ID da última pizza da lista e soma 1
        ultimo_id = max(p['id'] for p in pizzas)
        novo_id = ultimo_id + 1
    else:
        novo_id = 1
    
    nova_pizza['id'] = novo_id
    # ------------------------------

    pizzas.append(nova_pizza)
    salvar_dados(pizzas)
    return jsonify(nova_pizza), 201

# Deletar pizza
@app.route('/pizzas/<int:id>', methods=['DELETE'])
def excluir_sabor(id):
    pizzas = ler_dados()
    pizzas_filtradas = [p for p in pizzas if p['id'] != id]
    
    if len(pizzas_filtradas) == len(pizzas):
        return jsonify({"erro": "Pizza não encontrada"}), 404
        
    salvar_dados(pizzas_filtradas)
    return jsonify({"mensagem": "Removido com sucesso"})

if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)