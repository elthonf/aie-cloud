"""
Aula 5 / Atividade 2 — Treino LOCAL (no Cloud Shell) com tracking no MLflow do Workspace.

Treina um recomendador content-based de produtos QC usando embeddings (sentence-transformers)
+ NearestNeighbors (sklearn). Rastreia o experimento no MLflow integrado ao Azure ML Workspace
e registra o modelo no Model Registry.

NOTA pedagógica: este script roda LOCAL no Cloud Shell — útil para entender o que o MLflow
captura. A Atividade 3 (Job) faz o mesmo, mas rodando no Compute Cluster com environment
versionado.

Variáveis de ambiente necessárias:
    SUBSCRIPTION_ID   — id da subscription
    RESOURCE_GROUP    — nome do RG da Aula 5
    WORKSPACE_NAME    — nome do Workspace
    DATA_PATH         — caminho local do produtos.csv (default: ~/qc-aula05/produtos.csv)

Hiperparâmetros opcionais:
    N_NEIGHBORS       — número de vizinhos (default: 5)
    EMBEDDING_MODEL   — modelo de embedding (default: all-MiniLM-L6-v2)

Dependências:
    pip install --user mlflow azureml-mlflow azure-ai-ml azure-identity \\
                       sentence-transformers scikit-learn pandas
"""
import os
import pickle

import mlflow
import mlflow.pyfunc
import pandas as pd
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors


class RecomendadorPyfunc(mlflow.pyfunc.PythonModel):
    """Wrapper pyfunc: empacota nn + embeddings + df para servir via endpoint."""

    def load_context(self, context):
        import pickle
        with open(context.artifacts["modelo_pkl"], "rb") as f:
            obj = pickle.load(f)
        self.nn = obj["nn"]
        self.embeddings = obj["embeddings"]
        self.df = obj["df"]

    def predict(self, context, model_input):
        produto_id = int(model_input["produto_id"].iloc[0])
        n = int(model_input["n_recomendacoes"].iloc[0]) if "n_recomendacoes" in model_input.columns else 5
        query = self.embeddings[produto_id].reshape(1, -1)
        dists, idxs = self.nn.kneighbors(query, n_neighbors=min(n + 1, len(self.df)))
        vizinhos = [i for i in idxs[0] if i != produto_id][:n]
        scores = [float(1 - d) for i, d in zip(idxs[0], dists[0]) if i != produto_id][:n]
        rows = [
            {
                "produto_id": int(idx),
                "nome": str(self.df.iloc[idx]["nome"]),
                "categoria": str(self.df.iloc[idx]["categoria"]),
                "preco": float(self.df.iloc[idx]["preco"]),
                "score_similaridade": round(s, 4),
            }
            for idx, s in zip(vizinhos, scores)
        ]
        return pd.DataFrame(rows)


# === 1. Conectar no Azure ML Workspace ===
SUBSCRIPTION_ID = os.environ["SUBSCRIPTION_ID"]
RESOURCE_GROUP  = os.environ["RESOURCE_GROUP"]
WORKSPACE       = os.environ["WORKSPACE_NAME"]

credential = DefaultAzureCredential()
ml_client = MLClient(credential, SUBSCRIPTION_ID, RESOURCE_GROUP, WORKSPACE)

# Configura MLflow para apontar para o Workspace (tracking remoto)
mlflow.set_tracking_uri(ml_client.workspaces.get(WORKSPACE).mlflow_tracking_uri)
mlflow.set_experiment("recomendacao-qc")


# === 2. Hiperparâmetros (parametrizados via env vars) ===
N_NEIGHBORS = int(os.environ.get("N_NEIGHBORS", 5))
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
DATA_PATH = os.path.expanduser(
    os.environ.get("DATA_PATH", "~/qc-aula05/produtos.csv")
)


def main():
    with mlflow.start_run() as run:
        print(f"Run ID: {run.info.run_id}")

        # === 3. Log de params ===
        mlflow.log_param("n_neighbors", N_NEIGHBORS)
        mlflow.log_param("embedding_model", EMBEDDING_MODEL)
        mlflow.log_param("metric", "cosine")

        # === 4. Carregar dataset ===
        print(f"→ Carregando produtos de {DATA_PATH}...")
        df = pd.read_csv(DATA_PATH)
        mlflow.log_metric("num_produtos", len(df))
        print(f"✓ {len(df)} produtos carregados")

        # === 5. Gerar embeddings ===
        print(f"→ Gerando embeddings com {EMBEDDING_MODEL}...")
        model_emb = SentenceTransformer(EMBEDDING_MODEL)
        textos = (df["nome"] + ". " + df["descricao"]).tolist()
        embeddings = model_emb.encode(textos, show_progress_bar=False)
        mlflow.log_metric("embedding_dim", embeddings.shape[1])
        print(f"✓ Embeddings shape: {embeddings.shape}")

        # === 6. Treinar NearestNeighbors ===
        # +1 porque o próprio produto sai como vizinho 0 e queremos descartar
        print(f"→ Treinando NearestNeighbors com n={N_NEIGHBORS}...")
        nn = NearestNeighbors(n_neighbors=N_NEIGHBORS + 1, metric="cosine")
        nn.fit(embeddings)

        # === 7. Avaliação simplificada (precision proxy) ===
        # Para cada produto, os k vizinhos devem ser da mesma categoria > 50% do tempo.
        _, indices = nn.kneighbors(embeddings)
        same_cat = 0
        total = 0
        for i, vizinhos in enumerate(indices):
            cat_orig = df.iloc[i]["categoria"]
            for j in vizinhos[1:]:  # pula o próprio (índice 0)
                if df.iloc[j]["categoria"] == cat_orig:
                    same_cat += 1
                total += 1
        precision_proxy = same_cat / total
        mlflow.log_metric("precision_at_k_proxy", precision_proxy)
        print(f"✓ Precision proxy (mesma categoria): {precision_proxy:.3f}")

        # === 8. Serializar modelo + embeddings ===
        os.makedirs("./model_artifacts", exist_ok=True)
        with open("./model_artifacts/nn_model.pkl", "wb") as f:
            pickle.dump({"nn": nn, "embeddings": embeddings, "df": df}, f)

        # === 9. Registrar no Model Registry como pyfunc (nn + embeddings + df empacotados) ===
        # NearestNeighbors não tem predict() — pyfunc empacota o pkl completo para o endpoint.
        mlflow.pyfunc.log_model(
            artifact_path="pyfunc_model",
            python_model=RecomendadorPyfunc(),
            artifacts={"modelo_pkl": "./model_artifacts/nn_model.pkl"},
            registered_model_name="recomendador-qc",
        )

        print("✓ Modelo registrado no Registry como 'recomendador-qc'")
        print(f"  Veja no Studio: experimento 'recomendacao-qc' → run {run.info.run_id}")


if __name__ == "__main__":
    main()
