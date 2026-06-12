import pytest
import logging
import concurrent.futures

# Instanciando o logger para registrar os passos no terminal/relatório (deixando os logs mais claros e informativos)
logger = logging.getLogger(__name__)

# 1
@pytest.mark.smoke
def test_status_code_sucesso(response_rates):
    """Verifica se a API de Câmbio está online (Status 200)"""
    logger.info("🔎 [SMOKE TEST] Validando se o servidor da API está no ar (Status HTTP 200)...")
    assert response_rates.status_code == 200, f"Esperado 200, recebido {response_rates.status_code}"
    logger.info("✅ Servidor online e respondendo corretamente.")

# 2
@pytest.mark.performance
def test_tempo_de_resposta(response_rates):
    """Garante que a API responde em menos de 2 segundos (SLA)"""
    logger.info("⏱️ [PERFORMANCE] Medindo o tempo de resposta da requisição...")
    tempo_resposta_segundos = response_rates.elapsed.total_seconds()
    
    logger.info(f"📊 Tempo registrado: {tempo_resposta_segundos} segundos. Limite (SLA): 2.0s.")
    assert tempo_resposta_segundos < 2.0, f"SLA violado. Tempo: {tempo_resposta_segundos}s"
    logger.info("✅ Tempo de resposta dentro dos padrões de qualidade.")

# 3
@pytest.mark.contract
def test_verificacao_conteudo_json(response_rates):
    """Confirma que o sistema retorna um pacote de dados válido (Dicionário)"""
    logger.info("📦 [CONTRATO] Analisando a estrutura principal do pacote JSON recebido...")
    data = response_rates.json()
    
    assert isinstance(data, dict), "O formato de retorno deveria ser um dicionário."
    assert data.get("base") == "USD", "A moeda base retornada não confere com a solicitada."
    logger.info("✅ Estrutura principal validada com sucesso.")

# 4
@pytest.mark.contract
def test_validacao_campos_e_tipos(response_rates):
    """Valida se os campos obrigatórios (Base, Data e Taxas) existem no sistema"""
    logger.info("🏷️ [CONTRATO] Verificando a presença dos campos obrigatórios...")
    data = response_rates.json()
    
    campos_esperados = ["base", "date", "rates"]
    for campo in campos_esperados:
        assert campo in data, f"Campo obrigatório ausente: {campo}"
        
    assert isinstance(data["rates"], dict), "O campo 'rates' deveria ser um dicionário com as cotações."
    logger.info("✅ Todos os campos obrigatórios estão presentes.")

@pytest.mark.contract
@pytest.mark.parametrize("moeda_esperada", ["BRL", "EUR", "AUD", "JPY"])
def test_presenca_moedas_obrigatorias(response_rates, moeda_esperada):
    """Verifica se as moedas principais para conversão estão disponíveis"""
    logger.info(f"💰 [NEGÓCIO] Buscando a cotação da moeda obrigatória: {moeda_esperada}...")
    data = response_rates.json()
    taxas = data.get("rates", {})
    
    assert moeda_esperada in taxas, f"Moeda obrigatória ausente: {moeda_esperada}"
    logger.info(f"✅ Moeda {moeda_esperada} encontrada com a cotação atual de: {taxas[moeda_esperada]}")

# 5
@pytest.mark.error
def test_tratamento_falha_endpoint_invalido(api_client):
    """Garante que o sistema bloqueia consultas de moedas que não existem (Erro 404)"""
    logger.info("🛡️ [SEGURANÇA] Simulando requisição para moeda inexistente...")
    response = api_client.get_endpoint_invalido()
    
    logger.info(f"🛑 Status recebido: {response.status_code}. Esperado: 404.")
    assert response.status_code == 404, "A API deveria retornar 404 para bases não encontradas."
    logger.info("✅ Sistema tratou o erro corretamente.")

# 6
@pytest.mark.performance
def test_carga_simples_concorrencia(api_client):
    """Garante que a API suporta múltiplos acessos simultâneos sem cair"""
    logger.info("🚀 [CARGA] Iniciando teste de stress com 10 requisições simultâneas...")
    
    quantidade_requisicoes = 10
    resultados = []
    
    # Dispara as requisições todas ao mesmo tempo em paralelo usando Threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=quantidade_requisicoes) as executor:
        futures = [executor.submit(api_client.get_rates, "USD") for _ in range(quantidade_requisicoes)]
        
        for future in concurrent.futures.as_completed(futures):
            response = future.result()
            resultados.append(response.status_code)
            
    logger.info(f"📊 Status das requisições paralelas: {resultados}")
    
    # Verifica se o servidor derrubou ou falhou alguma conexão (Ex: Retornando 429 Too Many Requests ou 500)
    for status in resultados:
        assert status == 200, f"Falha no teste de carga. O servidor retornou o erro {status} sob stress."
        
    logger.info("✅ O servidor suportou o pico de acesso concorrente sem perda de pacotes.")