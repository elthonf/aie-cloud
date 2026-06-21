"""
Gera áudio WAV em PT-BR via Azure Speech TTS (REST API).
Uso: python3 gerar_audio_tts.py
Variáveis de ambiente:
    AI_KEY     — chave do AI Services (exportar do Key Vault: ver passo 1 da Atividade 2)
    AI_REGION  — região (default: eastus2)
Saída: /tmp/audio-teste.wav
"""
import os
import sys
import requests

AI_REGION = os.environ.get("AI_REGION", "eastus2")
AI_KEY    = os.environ.get("AI_KEY", "")

if not AI_KEY:
    print("Exporte AI_KEY com a chave primária do AI Services:")
    print("  export AI_KEY=$(az keyvault secret show --vault-name <KV_NAME> --name ai-services-key --query value -o tsv)")
    sys.exit(1)

SSML = """
<speak version='1.0' xml:lang='pt-BR'>
  <voice xml:lang='pt-BR' xml:gender='Male' name='pt-BR-AntonioNeural'>
    A Quantum Commerce é uma plataforma de e-commerce que opera em doze países.
    Nossos agentes de inteligência artificial ajudam clientes a encontrar produtos,
    calcular fretes, processar pedidos e responder dúvidas em tempo real.
    A nossa missão é tornar o comércio mais humano, inteligente e acessível.
  </voice>
</speak>
"""

tts_url = f"https://{AI_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
# Autenticação por chave: header Ocp-Apim-Subscription-Key (não Authorization)
headers = {
    "Ocp-Apim-Subscription-Key": AI_KEY,
    "Content-Type": "application/ssml+xml",
    "X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm",
}

print(f"Gerando áudio via TTS ({AI_REGION})...")
resp = requests.post(tts_url, headers=headers, data=SSML.encode("utf-8"), timeout=30)

if resp.status_code == 200:
    output_path = "/tmp/audio-teste.wav"
    with open(output_path, "wb") as f:
        f.write(resp.content)
    size_kb = len(resp.content) // 1024
    print(f"✓ Áudio salvo em {output_path} ({size_kb} KB)")
else:
    print(f"✗ Erro {resp.status_code}: {resp.text}")
    sys.exit(1)
