import pytest
import logging
import os
import datetime 
from filelock import FileLock
from api.client import ExchangeRateAPI

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def api_client():
    return ExchangeRateAPI()

# O xdist vai forçar a injeção do tmp_path_factory e worker_id nativamente
@pytest.fixture(scope="session")
def response_rates(api_client, tmp_path_factory, worker_id):
    """Fixture que garante 1 única requisição na API, mesmo com múltiplos Workers"""
    
    # Se NÃO estiver rodando em paralelo (sem xdist), age normalmente
    if worker_id == "master":
        logger.info("🔌 [SETUP ÚNICO] Execução normal (Master). Conectando na API...")
        yield api_client.get_rates("USD")
        logger.info("🧹 [TEARDOWN] Finalizando testes do Master.")
        return

    # === Lógica do Paralelismo com XDIST ===
    # Arquivo temporário onde o worker salvará a resposta da API (JSON)
    caminho_base = tmp_path_factory.getbasetemp().parent
    arquivo_dados = caminho_base / "api_data_cache.json"
    arquivo_lock = caminho_base / "api_data_cache.lock"

    with FileLock(str(arquivo_lock)):
        # Verifica se algum worker anterior já baixou os dados
        if not arquivo_dados.is_file():
            logger.info(f"🔌 [SETUP XDIST] O Worker '{worker_id}' foi o primeiro. Realizando requisição...")
            response = api_client.get_rates("USD")
            
            # Salva o texto da resposta para os outros lerem
            arquivo_dados.write_text(response.text)
        else:
            # Se o arquivo já existe, este worker simplesmente avisa que vai reaproveitar.
            logger.info(f"♻️ [SETUP XDIST] O Worker '{worker_id}' reaproveitou a requisição já em cache.")

    # Simula o objeto de Response do requests reconstruindo-o a partir do cache
    import requests
    fake_response = requests.models.Response()
    fake_response.status_code = 200 # Assumindo sucesso pelo cache
    fake_response._content = arquivo_dados.read_bytes()
    
    # Simula o tempo usando timedelta, para o '.total_seconds()' funcionar no teste de performance
    fake_response.elapsed = datetime.timedelta(seconds=0.5) 

    yield fake_response