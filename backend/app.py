from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import os

# Criação da aplicação Flask
app = Flask(__name__)

# Habilita CORS para permitir que o front consuma a API
CORS(app)

# Nome do arquivo onde os dados das pizzas ficam salvos
NOME_ARQUIVO = 'pizzas.json'

# Status permitidos no sistema
STATUS_VALIDOS = ["disponivel", "indisponivel", "promocao"]

# Tipos de pizzas permitidos no sistema
TIPOS_PIZZA = ["tradicional", "doce", "vegana","vegetariana","especial", "gourmet"]


# FUNÇÕES DE PERSISTÊNCIA
def ler_dados():
    # Se o arquivo não existir, cria um arquivo vazio
    # Isso garante persistência mesmo no primeiro uso
    if not os.path.exists(NOME_ARQUIVO):
        with open(NOME_ARQUIVO, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []

    # Abre o arquivo JSON e retorna os dados salvos
    with open(NOME_ARQUIVO, 'r', encoding='utf-8') as f:
        return json.load(f)


def salvar_dados(pizzas):
    # Salva a lista de pizzas no arquivo JSON
    # indent e ensure_ascii deixam o arquivo legível
    with open(NOME_ARQUIVO, 'w', encoding='utf-8') as f:
        json.dump(pizzas, f, indent=4, ensure_ascii=False)


# ROTA PARA CARREGAR O FRONT-END
@app.route('/')
def home():
    # Renderiza o arquivo index.html do frontend
    return render_template('index.html')


# LISTAR PIZZAS (READ)
@app.route('/pizzas', methods=['GET'])
def obter_sabores():
    # Retorna todas as pizzas cadastradas no sistema
    return jsonify(ler_dados()), 200


# ADICIONAR PIZZA (CREATE)
@app.route('/pizzas', methods=['POST'])
def adicionar_pizza():
    pizzas = ler_dados()
    nova_pizza = request.get_json()

    # Verifica se o JSON foi enviado corretamente
    if not nova_pizza:
        return jsonify({"erro": "JSON inválido"}), 400

    # Validação do nome
    if not nova_pizza.get("nome") or len(nova_pizza["nome"]) < 3:
        return jsonify({"erro": "Nome deve ter no mínimo 3 caracteres"}), 400


    # Validação do valor (não pode ser zero ou negativo)
    if not isinstance(nova_pizza.get("valor"), (int, float)) or nova_pizza["valor"] <= 0:
        return jsonify({"erro": "Valor deve ser maior que zero"}), 400

    # Validação do status (deve estar na lista permitida)
    if nova_pizza.get("status") not in STATUS_VALIDOS:
        return jsonify({
            "erro": "Status inválido",
            "status_validos": STATUS_VALIDOS
        }), 400

    # Validação do tipo da pizza (tradicional, doce, vegana, etc)
    if nova_pizza.get("tipo") not in TIPOS_PIZZA:
        return jsonify({
            "erro": "Tipo de pizza inválido",
            "tipos_validos": TIPOS_PIZZA
        }), 400

    # --- LÓGICA AUTO-INCREMENTO ---
    # Gera um novo ID baseado no maior ID existente
    novo_id = max([p["id"] for p in pizzas], default=0) + 1

    # Cria o objeto final da pizza
    pizza = {
        "id": novo_id,
        "nome": nova_pizza["nome"],
        "descricao": nova_pizza["descricao"],
        "valor": nova_pizza["valor"],
        "status": nova_pizza["status"],
        "tipo": nova_pizza["tipo"]
    }

    # Adiciona a nova pizza na lista
    pizzas.append(pizza)

    # Salva no arquivo JSON
    salvar_dados(pizzas)

    # Retorna a pizza criada
    return jsonify(pizza), 201


# EDITAR PIZZA (UPDATE)
@app.route('/pizzas/<int:id>', methods=['PUT'])
def editar_pizza(id):
    pizzas = ler_dados()
    dados = request.get_json()

    # Verifica se o JSON foi enviado
    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    # Procura a pizza pelo ID
    for pizza in pizzas:
        if pizza['id'] == id:

            # Mantém valores antigos caso não sejam enviados
            nome = dados.get("nome", pizza["nome"])
            descricao = dados.get("descricao", pizza["descricao"])
            valor = dados.get("valor", pizza["valor"])
            tipo = dados.get("tipo", pizza["tipo"])

            # Validações
            if not nome or len(nome) < 3:
                return jsonify({"erro": "Nome deve ter no mínimo 3 caracteres"}), 400
            

            if not isinstance(valor, (int, float)) or valor <= 0:
                return jsonify({"erro": "Valor inválido"}), 400

            

            # Atualiza os dados da pizza
            pizza["nome"] = nome
            pizza["descricao"] = descricao
            pizza["valor"] = valor
            pizza["tipo"] = tipo

            # Salva as alterações
            salvar_dados(pizzas)

            return jsonify(pizza), 200

    # Caso o ID não exista
    return jsonify({"erro": "Pizza não encontrada"}), 404


# ALTERAR SOMENTE O STATUS (PATCH)
@app.route('/pizzas/<int:id>/status', methods=['PATCH'])
def alterar_status(id):
    pizzas = ler_dados()
    dados = request.get_json()

    # Verifica se o status foi enviado
    if not dados or "status" not in dados:
        return jsonify({"erro": "Status é obrigatório"}), 400

    # Valida se o status é permitido
    if dados["status"] not in STATUS_VALIDOS:
        return jsonify({
            "erro": "Status inválido",
            "status_validos": STATUS_VALIDOS
        }), 400

    # Procura a pizza e altera apenas o status
    for pizza in pizzas:
        if pizza["id"] == id:
            pizza["status"] = dados["status"]
            salvar_dados(pizzas)
            return jsonify(pizza), 200

    return jsonify({"erro": "Pizza não encontrada"}), 404


# DELETAR PIZZA
@app.route('/pizzas/<int:id>', methods=['DELETE'])
def excluir_sabor(id):
    pizzas = ler_dados()

    # Remove a pizza com o ID informado
    pizzas_filtradas = [p for p in pizzas if p['id'] != id]

    # Se nenhuma pizza foi removida, o ID não existe
    if len(pizzas_filtradas) == len(pizzas):
        return jsonify({"erro": "Pizza não encontrada"}), 404

    # Salva a lista atualizada
    salvar_dados(pizzas_filtradas)

    return jsonify({"mensagem": "Removido com sucesso"}), 200


if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)
