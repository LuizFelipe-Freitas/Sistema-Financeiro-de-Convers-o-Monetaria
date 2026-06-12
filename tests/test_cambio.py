import pytest
from api.client import ExchangeRateAPI

api = ExchangeRateAPI()

@pytest.fixture(scope="module")
def response_rates():
    """Executa a requisição apenas uma vez por execução dos testes."""
    return api.get_rates("USD")

@pytest.mark.smoke
def test_status_code_sucesso(response_rates):
    """Verifica se a API de Câmbio está online (Status 200)"""
    assert response_rates.status_code == 200, f"Esperado 200, recebido {response_rates.status_code}"

@pytest.mark.performance
def test_tempo_de_resposta(response_rates):
    """Garante que a API responde em menos de 2 segundos (SLA)"""
    tempo_resposta_segundos = response_rates.elapsed.total_seconds()
    assert tempo_resposta_segundos < 2.0, f"SLA violado. Tempo: {tempo_resposta_segundos}s"

@pytest.mark.contract
def test_verificacao_conteudo_json(response_rates):
    """Confirma que o sistema retorna um pacote de dados válido (Dicionário)"""
    data = response_rates.json()
    assert isinstance(data, dict), "O formato de retorno deveria ser um dicionário."
    assert data.get("base") == "USD", "A moeda base retornada não confere com a solicitada."

@pytest.mark.contract
def test_validacao_campos_e_tipos(response_rates):
    """Valida se os campos obrigatórios (Base, Data e Taxas) existem no sistema"""
    data = response_rates.json()
    
    campos_esperados = ["base", "date", "rates"]
    for campo in campos_esperados:
        assert campo in data, f"Campo obrigatório ausente: {campo}"
        
    assert isinstance(data["rates"], dict), "O campo 'rates' deveria ser um dicionário com as cotações."

@pytest.mark.contract
@pytest.mark.parametrize("moeda_esperada", ["BRL", "EUR", "AUD", "JPY"])
def test_presenca_moedas_obrigatorias(response_rates, moeda_esperada):
    """Verifica se as moedas principais para conversão estão disponíveis"""
    data = response_rates.json()
    taxas = data.get("rates", {})
    
    assert moeda_esperada in taxas, f"Moeda obrigatória ausente: {moeda_esperada}"
    assert isinstance(taxas[moeda_esperada], (int, float)), f"A taxa de {moeda_esperada} deveria ser numérica."

@pytest.mark.error
def test_tratamento_falha_endpoint_invalido():
    """Garante que o sistema bloqueia consultas de moedas que não existem (Erro 404)"""
    response = api.get_endpoint_invalido()
    assert response.status_code == 404, "A API deveria retornar 404 para bases não encontradas."