"""
Function App — Aula 4 Quantum Commerce
Rotas cognitivas via Managed Identity (Language, Vision) e Key Vault (Speech):
  GET  /api/health
  GET  /api/transcrever?blob=<nome>&container=audios&idioma=pt-BR
  POST /api/analisar-reviews?limit=10
  GET  /api/analisar-imagem?blob=<nome>&container=imagens
"""
import json
import logging
import os
import requests
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

AI_ENDPOINT          = os.environ["AI_ENDPOINT"]
AI_REGION            = os.environ.get("AI_REGION", "eastus2")
AI_KEY               = os.environ.get("AI_KEY", "")  # Key Vault reference resolvida pelo runtime
DATA_STORAGE_ACCOUNT = os.environ["DATA_STORAGE_ACCOUNT"]
MONGODB_URI          = os.environ["MONGODB_URI"]

_credential = DefaultAzureCredential()
_blob_service = BlobServiceClient(
    f"https://{DATA_STORAGE_ACCOUNT}.blob.core.windows.net",
    credential=_credential,
)


def _get_speech_token(region: str) -> str:
    """
    Troca a subscription key (do Key Vault) por speech token.
    Speech exige a role 'Cognitive Services Speech User' para MI — usamos key por simplicidade.
    """
    resp = requests.post(
        f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken",
        headers={"Ocp-Apim-Subscription-Key": AI_KEY, "Content-Length": "0"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.text


@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({
            "status": "ok",
            "service": "qc-cognitive",
            "rotas": ["/api/health", "/api/transcrever", "/api/analisar-reviews", "/api/analisar-imagem"],
            "ai_endpoint": AI_ENDPOINT,
        }),
        mimetype="application/json",
    )


@app.route(route="transcrever", methods=["GET", "POST"])
def transcrever(req: func.HttpRequest) -> func.HttpResponse:
    """
    Transcreve áudio WAV do Blob via Azure Speech STT (REST API).
    GET /api/transcrever?blob=audio-teste.wav&idioma=pt-BR
    """
    blob_name = req.params.get("blob", "audio-teste.wav")
    container = req.params.get("container", "audios")
    idioma    = req.params.get("idioma", "pt-BR")

    try:
        # 1. Baixar áudio do Blob via MI
        blob_client = _blob_service.get_blob_client(container=container, blob=blob_name)
        audio_bytes = blob_client.download_blob().readall()

        # 2. Obter speech token via key (do Key Vault)
        token = _get_speech_token(AI_REGION)
        resp = requests.post(
            f"https://{AI_REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
                "Accept": "application/json",
            },
            params={"language": idioma, "format": "detailed"},
            data=audio_bytes,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        transcricao = ""
        if "NBest" in data and data["NBest"]:
            transcricao = data["NBest"][0].get("Display", "")
        elif "DisplayText" in data:
            transcricao = data["DisplayText"]

        return func.HttpResponse(
            json.dumps({
                "transcricao": transcricao,
                "idioma": idioma,
                "blob": blob_name,
                "status_stt": data.get("RecognitionStatus", ""),
            }, ensure_ascii=False),
            mimetype="application/json",
        )
    except Exception as e:
        logging.exception("Falha em /transcrever")
        return func.HttpResponse(json.dumps({"erro": str(e)}), mimetype="application/json", status_code=500)


@app.route(route="analisar-reviews", methods=["GET", "POST"])
def analisar_reviews(req: func.HttpRequest) -> func.HttpResponse:
    """
    Lê reviews do MongoDB, analisa sentimento + entidades via Language (MI),
    e atualiza os documentos com os resultados.
    POST /api/analisar-reviews?limit=10
    """
    limit = int(req.params.get("limit", 10))

    try:
        from pymongo import MongoClient
        from azure.ai.textanalytics import TextAnalyticsClient

        # 1. MongoDB
        mongo = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        col = mongo["qc-db"]["reviews"]

        items = list(col.find({"sentimento_label": {"$exists": False}}).limit(limit))
        if not items:
            return func.HttpResponse(
                json.dumps({"msg": "Nenhuma review nova para analisar. Todas já processadas."}),
                mimetype="application/json",
            )

        # 2. Language via MI
        ta_client = TextAnalyticsClient(endpoint=AI_ENDPOINT, credential=_credential)
        documentos = [item["texto"] for item in items]

        # 3. Batch de no máximo 5 (limite do tier S0)
        BATCH_SIZE = 5
        sentimentos, entidades = [], []
        for i in range(0, len(documentos), BATCH_SIZE):
            batch = documentos[i:i + BATCH_SIZE]
            sentimentos.extend(ta_client.analyze_sentiment(batch, language="pt"))
            entidades.extend(ta_client.recognize_entities(batch, language="pt"))

        # 4. Atualizar MongoDB
        resultados = []
        for i, item in enumerate(items):
            sent = sentimentos[i]
            ent  = entidades[i]
            if sent.is_error or ent.is_error:
                continue
            update = {
                "sentimento_label": sent.sentiment,
                "sentimento_score": {
                    "positive": round(sent.confidence_scores.positive, 3),
                    "neutral":  round(sent.confidence_scores.neutral,  3),
                    "negative": round(sent.confidence_scores.negative, 3),
                },
                "entidades": [
                    {"text": e.text, "category": e.category, "confidence": round(e.confidence_score, 3)}
                    for e in ent.entities
                ],
            }
            col.update_one({"_id": item["_id"]}, {"$set": update})
            resultados.append({"id": item.get("id"), "produto": item.get("produto"), "sentimento": sent.sentiment})

        positivos = sum(1 for r in resultados if r["sentimento"] == "positive")
        negativos = sum(1 for r in resultados if r["sentimento"] == "negative")

        return func.HttpResponse(
            json.dumps({
                "total_analisadas": len(resultados),
                "positivas": positivos,
                "negativas": negativos,
                "neutras":   len(resultados) - positivos - negativos,
                "exemplos":  resultados[:3],
            }, ensure_ascii=False),
            mimetype="application/json",
        )
    except Exception as e:
        logging.exception("Falha em /analisar-reviews")
        return func.HttpResponse(json.dumps({"erro": str(e)}), mimetype="application/json", status_code=500)


@app.route(route="analisar-imagem", methods=["GET", "POST"])
def analisar_imagem(req: func.HttpRequest) -> func.HttpResponse:
    """
    Analisa imagem do Blob com Vision 4.0 (Tags + OCR + Objects) via MI.
    GET /api/analisar-imagem?blob=produto.jpg
    """
    blob_name = req.params.get("blob", "produto.jpg")
    container = req.params.get("container", "imagens")

    try:
        from azure.ai.vision.imageanalysis import ImageAnalysisClient
        from azure.ai.vision.imageanalysis.models import VisualFeatures

        # 1. Baixar imagem do Blob via MI
        blob_client = _blob_service.get_blob_client(container=container, blob=blob_name)
        image_data = blob_client.download_blob().readall()

        # 2. Vision 4.0 via MI
        vision_client = ImageAnalysisClient(endpoint=AI_ENDPOINT, credential=_credential)

        # Caption não disponível em eastus2 — usar DENSE_CAPTIONS em eastus/westus2/westeurope
        result = vision_client.analyze(
            image_data=image_data,
            visual_features=[VisualFeatures.TAGS, VisualFeatures.READ, VisualFeatures.OBJECTS],
        )

        tags = [{"name": t.name, "confidence": round(t.confidence, 3)} for t in (result.tags.list if result.tags else [])]
        texto_extraido = ""
        if result.read:
            texto_extraido = "\n".join(line.text for block in result.read.blocks for line in block.lines)

        objetos = []
        if result.objects and result.objects.list:
            for obj in result.objects.list:
                box = obj.bounding_box
                objetos.append({"label": obj.tags[0].name if obj.tags else "obj",
                                 "box": {"x": box.x, "y": box.y, "w": box.width, "h": box.height}})

        return func.HttpResponse(
            json.dumps({"caption": "", "tags": tags[:10], "texto_extraido": texto_extraido,
                        "objetos_detectados": objetos, "blob": blob_name}, ensure_ascii=False),
            mimetype="application/json",
        )
    except Exception as e:
        logging.exception("Falha em /analisar-imagem")
        return func.HttpResponse(json.dumps({"erro": str(e)}), mimetype="application/json", status_code=500)
