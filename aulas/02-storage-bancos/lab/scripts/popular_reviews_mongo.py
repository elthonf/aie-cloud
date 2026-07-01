"""
Aula 2 / Atividade 3-A (alternativa) — Inserir 30 reviews fictícias da QC no MongoDB.

Alternativa ao popular_reviews.py (Cosmos DB) para quando o Cosmos não está disponível
na região. Mesma estrutura de dados e mesmo random seed — facilita comparar os dois
bancos de dados NoSQL lado a lado.

Variável de ambiente necessária:
    MONGO_IP  — IP público do ACI (terraform output -raw mongodb_public_ip)

Dependências (instaladas automaticamente se ausentes):
    pymongo
"""

import os
import random
import sys
import time

MONGO_IP = os.environ.get("MONGO_IP")
if not MONGO_IP:
    print("Exporte MONGO_IP com o IP do ACI:")
    print("  export MONGO_IP=$(terraform output -raw mongodb_public_ip)")
    sys.exit(1)

try:
    from pymongo import MongoClient, errors
except ImportError:
    print("Instalando pymongo...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pymongo", "-q"])
    from pymongo import MongoClient, errors

# Mesmo TEMPLATES e random.seed do popular_reviews.py — dados idênticos nos dois bancos.
TEMPLATES = [
    ("Adorei! Chegou rápido e funcionou perfeitamente.", 5),
    ("Produto excelente, recomendo demais.", 5),
    ("Cumpre o que promete, vale a pena pelo preço.", 4),
    ("Bom produto, mas a embalagem chegou amassada.", 4),
    ("Funciona ok, nada de especial.", 3),
    ("Esperava mais pelo valor pago.", 2),
    ("Decepcionante, não recomendo.", 1),
    ("Veio com defeito, tive que trocar.", 1),
    ("Maravilhoso, superou expectativas!", 5),
    ("Compraria de novo, ótimo custo-benefício.", 5),
]

URI = f"mongodb://admin:QCadmin2024!@{MONGO_IP}:27017/?authSource=admin"

print(f"Conectando ao MongoDB em {MONGO_IP}:27017...")
for tentativa in range(10):
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✓ MongoDB pronto!")
        break
    except errors.ServerSelectionTimeoutError:
        print(f"  Aguardando MongoDB... (tentativa {tentativa+1}/10)")
        time.sleep(10)
else:
    print("✗ MongoDB não respondeu após 100s")
    sys.exit(1)

db = client["qc-db"]
col = db["reviews"]

# Limpar reviews existentes (idempotente)
col.delete_many({})

print(f"→ Inserindo 30 reviews em {MONGO_IP}/qc-db.reviews...")

random.seed(42)
docs = []
for i in range(1, 31):
    produto_id = str(random.randint(1, 20))
    texto, score = random.choice(TEMPLATES)
    docs.append({
        "id": f"r-{i:03d}",
        "produto_id": produto_id,
        "score": score,
        "texto": texto,
        "cliente": f"cliente-{random.randint(100, 999)}",
    })

result = col.insert_many(docs)
print(f"✓ {len(result.inserted_ids)} reviews inseridas")

# Query: reviews positivas do produto 5 (mesma query do popular_reviews.py)
print("\n=== Reviews 4+ do produto 5 ===")
for r in col.find({"produto_id": "5", "score": {"$gte": 4}}, {"_id": 0}):
    print(f"  [score {r['score']}] {r['texto']}")

print(f"\nExplore visualmente: http://{MONGO_IP}:8081")
print("(abre direto no browser, sem login)")

client.close()
