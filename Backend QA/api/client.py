import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExchangeRateAPI:
    def __init__(self):
        # Usando USD como base para os testes
        self.base_url = "https://api.exchangerate-api.com/v4/latest"

    def get_rates(self, base_currency="USD"):
        """Retorna as taxas de câmbio baseadas na moeda informada."""
        endpoint = f"{self.base_url}/{base_currency}"
        logger.info(f"Fazendo requisição GET para {endpoint}")
        return requests.get(endpoint)

    def get_endpoint_invalido(self):
        """Simula um endpoint inexistente para testar tratamento de erros."""
        endpoint = f"{self.base_url}/MOEDA_INEXISTENTE_QA"
        return requests.get(endpoint)