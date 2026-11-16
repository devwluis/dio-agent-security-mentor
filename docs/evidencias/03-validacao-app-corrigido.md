# Evidência 3: validação do app_corrigido.py

Modelo: deepseek-v4-flash-vision-exp (provider DeepSeek), Hermes v0.21.5.

## Prompt

> Releia o app_corrigido.py como especialista em AppSec. A consulta agora é
> parametrizada. Faça uma nova varredura e confirme se o SQL Injection foi
> mitigado ou se resta alguma falha.

## Resultado: SQL Injection mitigado, confirmado na prática

O agente executou uma varredura com as duas versões lado a lado, em bancos
separados, com os mesmos payloads.

| Payload | app.py (antes) | app_corrigido.py (depois) |
|---|---|---|
| ' OR '1'='1 | 200 login | 401 |
| admin' -- | 200 login | 401 |
| admin' OR '1'='1 | 200 login | 401 |
| UNION SELECT | 200 login | 401 |
| admin'; DROP ... | 500 | 401 |
| admin / admin123 (legítima) | 200 login | 200 login |

Causa raiz fechada: o ? faz o SQLite tratar a entrada como valor. A senha
também saiu do SQL e passou a usar check_password_hash.

## Falhas que ainda restam (formato impacto, probabilidade, severidade)

1. Enumeração de usuários por timing (MITRE T1589.001).
   Usuário existente levou cerca de 124 ms e inexistente cerca de 0,5 ms.
   Impacto: confidencialidade. Probabilidade: alta. Severidade: média.
2. Sem limite de tentativas de login (MITRE T1110.001).
   30 tentativas seguidas deram 30 respostas 401 e nenhuma 429.
   Impacto: integridade e confidencialidade. Probabilidade: alta.
   Severidade: alta se exposto, baixa em laboratório isolado.
3. Credenciais sem TLS no transporte.
   Hoje preso a 127.0.0.1, então não explorável. Severidade: baixa hoje,
   média se exposto.

Observação, não falha: o nome do usuário volta cru na resposta JSON. Viraria
XSS refletido se a saída passasse a ser HTML sem escape.

## O que esta evidência mostra

O agente validou a correção com teste real e, em vez de declarar o app
seguro, apontou o que resta no mesmo formato de análise em todos os casos.
