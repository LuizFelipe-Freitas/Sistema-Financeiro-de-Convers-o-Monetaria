     // Mapeamento dos elementos da interface
        const originSelect = document.getElementById('origem');
        const targetSelect = document.getElementById('destino');
        const amountInput = document.getElementById('valor');
        const resultDiv = document.getElementById('resultado');
        const btnConverter = document.getElementById('btn-converter');

        // Moedas corporativas comumente usadas no cenário de Fintech
        const moedasDisponiveis = {
            "USD": "Dólar Americano",
            "BRL": "Real Brasileiro",
            "EUR": "Euro",
            "GBP": "Libra Esterlina",
            "JPY": "Iene Japonês",
            "AUD": "Dólar Australiano",
            "CAD": "Dólar Canadense"
        };

        // Função que insere as moedas no menu Dropdown quando a tela carrega
        function inicializarInterface() {
            for (const [codigo, nome] of Object.entries(moedasDisponiveis)) {
                const text = `${codigo} - ${nome}`;
                originSelect.add(new Option(text, codigo));
                targetSelect.add(new Option(text, codigo));
            }
            // Deixa USD -> BRL pré-selecionado como padrão
            originSelect.value = "USD";
            targetSelect.value = "BRL";
        }

        // Função central para consumo da API e renderização
        async function converterMoeda() {
            const amount = parseFloat(amountInput.value);
            const from = originSelect.value;
            const to = targetSelect.value;

            // Validação de segurança básica na interface
            if (isNaN(amount) || amount <= 0) {
                resultDiv.innerHTML = '<span style="color: #ef4444; font-weight: 600;">⚠️ Por favor, insira um valor válido.</span>';
                return;
            }

            // Atualiza o estado visual para carregamento
            btnConverter.disabled = true;
            btnConverter.innerText = "Consultando API...";

            try {
                // Requisição assíncrona HTTP
                const response = await fetch(`https://api.exchangerate-api.com/v4/latest/${from}`);
                const data = await response.json();
                
                // Cálculo de conversão
                const rate = data.rates[to];
                const finalValue = (amount * rate).toFixed(2);

                // Formatação monetária limpa para o usuário final
                resultDiv.innerHTML = `
                    <div class="amount">${amount.toLocaleString('pt-BR', {minimumFractionDigits: 2})} ${from} equivale a</div>
                    <div class="converted">${parseFloat(finalValue).toLocaleString('pt-BR', {minimumFractionDigits: 2})} ${to}</div>
                `;
            } catch (error) {
                // Tratamento de falha conforme vimos nos requisitos de QA
                resultDiv.innerHTML = '<span style="color: #ef4444; font-weight: 600;">Falha de integração. Tente novamente mais tarde.</span>';
            } finally {
                // Restaura o estado original do botão
                btnConverter.disabled = false;
                btnConverter.innerText = "Processar Conversão";
            }
        }

        // Ouve o Enter no teclado para disparar a conversão também
        amountInput.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                converterMoeda();
            }
        });

        // Executa a carga das opções na primeira vez
        window.onload = inicializarInterface;