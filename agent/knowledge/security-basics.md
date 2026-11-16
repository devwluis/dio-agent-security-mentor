# Fundamentos de segurança

Vocabulário e critérios mínimos para o agente conduzir uma análise de segurança consistente, em vez de reagir com uma correção genérica.

## Vulnerabilidade

Falha ou fraqueza em um sistema, processo ou configuração que pode ser explorada para comprometer a confidencialidade, a integridade ou a disponibilidade. Exemplos: entrada do usuário sem validação em uma query SQL, dependência desatualizada com CVE conhecida, credencial padrão não alterada.

## Ameaça

Qualquer agente (pessoa, grupo, script automatizado) ou evento com potencial de explorar uma vulnerabilidade. Uma vulnerabilidade sem ameaça plausível tem risco baixo. A mesma vulnerabilidade exposta à internet, com exploit público, tem risco alto.

## Risco

Risco = probabilidade de a ameaça se concretizar × impacto se ela se concretizar. Não é a vulnerabilidade em si, e sim a combinação dela com o contexto: quem pode explorar, com que facilidade e o que está em jogo.

## Tríade CIA

- **Confidencialidade:** só quem tem permissão acessa a informação.
- **Integridade:** a informação não é alterada sem autorização ou detecção.
- **Disponibilidade:** o sistema e o dado estão acessíveis quando necessário.

Toda vulnerabilidade analisada deve ser enquadrada em pelo menos um desses pilares. Isso explica o impacto em termos concretos, não só "é perigoso".

## Boas práticas defensivas

- **Validação de entrada:** nunca confiar em dado vindo do usuário; validar tipo, formato e tamanho.
- **Consultas parametrizadas:** nunca concatenar entrada do usuário em SQL, comandos de shell ou queries NoSQL.
- **Menor privilégio:** cada usuário, processo ou serviço só acessa o mínimo necessário.
- **Defesa em profundidade:** nenhuma camada isolada basta; combine várias.
- **MFA:** reduz o impacto de uma senha comprometida.
- **Gestão de segredos:** nunca commitar senha, token ou chave em texto puro.
- **Dependências atualizadas:** versões antigas carregam CVEs já corrigidas.
- **Logs e monitoramento:** tentativas de login falhas e comandos anômalos devem gerar alerta.

## Frameworks de referência

- **OWASP Top 10:** categorias mais comuns de falha em aplicações web (Injection, Broken Access Control etc.). Serve para classificar a falha.
- **MITRE ATT&CK:** catálogo de técnicas reais de ataque, cada uma com um ID (ex.: T1190, Exploit Public-Facing Application). Conecta a falha a um comportamento adversário documentado.
