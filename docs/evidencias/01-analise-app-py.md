# Evidência 1: análise do app.py com a skill vulnerability-analysis

Teste feito no Hermes Agent v0.21.5, rodando na raiz do repositório
(`hermes` aberto em `dio-agent-guardai/`), em ambiente de laboratório próprio.
O `app.py` é um login deliberadamente vulnerável, só para teste.

## Prompt enviado

> Atue como especialista em AppSec. Analise o app.py deste projeto: encontre a
> falha, explique como ela seria explorada, cite a técnica do MITRE ATT&CK e me
> diga o impacto, a probabilidade e a severidade. Não reescreva o código ainda:
> quero entender o raciocínio primeiro.

## Rastro das ferramentas (o agente foi buscar a skill do projeto)

```text
┊ 🔎 find      app.py  0.2s
┊ 📖 read      SKILL.md  0.1s
┊ 📖 read      app.py  0.0s
```

O agente encontrou a linha da skill na tabela do `AGENTS.md`, leu o
`skills/vulnerability-analysis/SKILL.md` e só depois leu o `app.py`.
Ele confirmou o contexto de laboratório pelo docstring do arquivo e, como a
skill manda, não repetiu a pergunta.

## Resposta do agente

Contexto confirmado: o próprio docstring do arquivo diz que é uma aplicação de laboratório (desafio GuardAI/DIO), então seguimos só com análise — sem payloads prontos e sem mexer no código, como você pediu. Aqui está o raciocínio completo.

O QUE FOI ENCONTRADO

Falha: SQL Injection (CWE-89, OWASP A03:2021 — Injection) na rota /login (app.py:41-44).

A causa raiz é a concatenação das entradas usuario e senha direto na string SQL. O problema não é o SQLite nem o Flask: é que a entrada do usuário entra na query sem nenhuma separação entre dado e código. Toda string SQL é montada assim:

  SELECT * FROM usuarios WHERE usuario = '<entrada>' AND senha = '<entrada>'

O banco interpreta as aspas simples como delimitadores de string. Quando o atacante envia uma aspa na entrada, ele "fecha" a string que a aplicação abriu e o que vier depois é interpretado pelo SQL como sintaxe, não como texto. É como alguém abrir aspas num texto de verdade: a partir daquele ponto, a pessoa que lê não sabe mais o que é citação e o que é fala dela.

Como seria explorada (o raciocínio, sem payload)

1. Bypass de autenticação. No campo de senha, o atacante manda algo na forma: fechar a string, quebrar a condição com OR e deixar a expressão sempre verdadeira (ex.: uma entrada que termine a query como senha = '' OR condição sempre-verdadeira). A query vira, na prática:

  WHERE usuario = 'qualquer_coisa' AND senha = '' OR verdadeiro

  Como OR verdadeiro vale para qualquer linha, o fetchone() (app.py:48) devolve a primeira linha da tabela — o admin, único usuário cadastrado — e o if resultado (app.py:51) é verdadeiro. Login efetuado como admin sem saber a senha.

2. Leitura completa do banco (blind SQLi). O app não devolve as linhas da tabela na resposta — ele só responde "ok" ou "erro" — mas isso é suficiente: a resposta é um oráculo booleano. O atacante pergunta ao banco, um caractere por vez, "este caractere da senha é X?", e a resposta ok/erro confirma ou nega. Assim ele extrai a tabela inteira (id, usuario, senha), inclusive via UNION com o número certo de colunas (3). Demora mais que o bypass, mas é automatizável em segundos.

3. Resultado do roubo. A senha admin123 está em texto puro (app.py:28-30) — se o atacante extrai a tabela, ele não precisa quebrar hash nenhum: ganha a credencial pronta.

Uma observação secundária: a mensagem "Bem-vindo, {usuario}!" ecoa a entrada sem escape (app.py:52). Como a resposta é JSON, o risco real depende de algum front-end renderizar esse conteúdo como HTML — vale anotar, mas não é a falha principal.

TÉCNICA NO MITRE ATT&CK

- T1190 — Exploit Public-Facing Application: é a técnica canônica para explorar vulnerabilidade conhecida (SQLi) em aplicação exposta; é o ponto de entrada (Initial Access). Como qualquer input HTTP chega à query, a superfície de ataque é o endpoint de login em si.
- Em seguida na cadeia: T1078 (Valid Accounts) — o atacante opera como admin legítimo após o bypass; e T1552.001 (Unsecured Credentials: Credentials in Files) — a credencial em texto puro guardada no banco.

AVALIAÇÃO DE RISCO

- Impacto: ALTO. Confidencialidade comprometida (leitura total do banco, inclusive credenciais), Integridade comprometida (login como admin; com acesso à tabela, no mínimo adulteração de dados — o sqlite3 não permite empilhar statements no mesmo execute, então a escrita direta via injeção é limitada, mas o desvio de autenticação já entrega a conta). Disponibilidade pouco afetada.
- Probabilidade: ALTA se alcançável. Exploração trivial, sem ferramenta especializada — é o exemplo clássico de injeção, conhecido há décadas, com exploit público em qualquer curso/cheatsheet. O único fator que segura a exposição é o bind em 127.0.0.1 (app.py:58), que limita a rede local; mas qualquer deploy que remova esse bind, ou um proxy na frente, expõe tudo.
- Severidade: CRÍTICA se o serviço ficar acessível em rede (na faixa de CVSS 9.0+, pois é remoto, sem autenticação prévia e sem interação do usuário — AV:N/AC:L/PR:N/UI:N); ALTA no cenário padrão do laboratório (localhost), onde o atacante precisaria de um ponto de apoio local para chegar até a porta.

Por que é grave e não "só um exercício": injeção não é um bug de lógica que falha às vezes — é a entrega do controle da query ao atacante. Neste caso específico, a senha em texto puro converte o SQLi em acesso direto à conta admin, e o oráculo booleano converte "só bypass" em "dump do banco".

Resumo no formato da skill:

  Falha: SQL Injection (CWE-89 / OWASP A03:2021-Injection)
  Contexto: /login (app.py:41-44), entrada concatenada na query SQLite
  Técnica (MITRE ATT&CK): T1190 Exploit Public-Facing Application (cadeia: T1078, T1552.001)
  Impacto: Confidencialidade e Integridade — bypass total de autenticação e leitura do banco
  Probabilidade: Alta (exploração trivial; atenuada só pelo bind em 127.0.0.1)
  Severidade: Crítica em rede / Alta no lab local
  Correção recomendada: (a seguir, quando você quiser)
  Como validar: (a seguir, quando você quiser)

Quando quiser partir para a correção, o caminho é o que esta skill chama de tratar a causa raiz, não o sintoma: parametrização da query — nunca mais montar SQL por concatenação. Me avisa se quer que eu explique o porquê da parametrização funcionar antes de mostrar o código, ou se já pode vir a solução com o passo de validação.
