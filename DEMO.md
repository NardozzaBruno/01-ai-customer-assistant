# Demonstração guiada

Roteiro para conhecer o projeto ou apresentar uma demonstração curta no portfólio.

## O problema e a proposta

Um pedido de banho ou tosa precisa de informações como serviço, porte do pet e
dia desejado. O protótipo organiza essa coleta em uma conversa, aproveita dados
já informados e permite revisar o resumo antes de concluir a solicitação.

É uma demonstração local baseada em regras. Não consulta agenda, não informa
preços e não envia solicitações ao pet shop.

## Antes de começar

Tenha Python 3.12 instalado e abra um terminal na pasta do projeto.
Execute:

```powershell
python main.py
```

Não é necessário instalar pacotes ou configurar uma chave de API.
Se o terminal estiver em `C:\WINDOWS\System32`, abra a pasta do projeto no
Explorador de Arquivos, clique com o botão direito no espaço vazio e escolha
**Abrir no Terminal** antes de executar o comando.

## Roteiro de apresentação: cerca de dois minutos

1. Diga `quero banho`: o assistente pergunta o porte.
2. Responda `meu pet e pequeno`: ele guarda o porte e pergunta apenas o dia.
3. Responda `pode ser amanha`: aparece o resumo com a data completa.
4. Digite `grande`: o porte muda e o serviço e a data são preservados.
5. Digite `confirmar`: a solicitação é concluída apenas na demonstração.
6. Digite `sair` para encerrar.

Durante a apresentação, destaque a coleta de dados, a memória da conversa,
a validação da data e a possibilidade de corrigir o resumo.

## Exemplo real das respostas

A transcrição abaixo foi gerada pelo código com a data de referência fixa em
**27/10/2026**. Na execução interativa, `amanha` usa a data atual de São Paulo.
Foram omitidos os avisos iniciais e as linhas de categoria do terminal.

```text
Cliente: quero banho
Assistente: Certo, banho! Qual é o porte do seu pet (pequeno, médio ou grande)?

Cliente: meu pet e pequeno
Assistente: Para qual dia? Responda hoje, amanhã, um dia da semana ou uma data (dia/mês/ano).

Cliente: pode ser amanha
Assistente: Resumo da solicitação: Banho; porte pequeno; dia desejado: amanhã (28/10/2026). Agendamento não confirmado: depende da disponibilidade do pet shop. Confira os dados. Digite 'confirmar' para concluir a solicitação, informe outro serviço, porte ou dia para corrigir, ou digite 'cancelar' para descartar.

Cliente: grande
Assistente: Resumo da solicitação: Banho; porte grande; dia desejado: amanhã (28/10/2026). Agendamento não confirmado: depende da disponibilidade do pet shop. Confira os dados. Digite 'confirmar' para concluir a solicitação, informe outro serviço, porte ou dia para corrigir, ou digite 'cancelar' para descartar.

Cliente: confirmar
Assistente: Resumo da solicitação: Banho; porte grande; dia desejado: amanhã (28/10/2026). Agendamento não confirmado: depende da disponibilidade do pet shop. Solicitação revisada e concluída nesta demonstração. Nada foi enviado ao pet shop. Para iniciar outra, informe o serviço.
```

## Outros cenários para experimentar

Comece cada cenário digitando `cancelar`, para descartar os dados anteriores.

| Digite | O que observar |
| --- | --- |
| `quero banho para um pet grande amanha` | O resumo aparece sem perguntas adicionais. |
| `nao quero banho, so tosa, pet pequeno amanha` | A solicitação contém apenas tosa. |
| `banho pequeno amanha ou sexta` | O assistente pede esclarecimento. |
| `banho pequeno 31/11` | A data inválida é rejeitada. |
| `cancelar` | A solicitação em andamento é descartada. |

## Como descrever o projeto

Desenvolvi um protótipo de atendimento em Python para organizar solicitações
de banho e tosa. Ele identifica o serviço, coleta porte e data, mantém o contexto
da conversa e permite corrigir um resumo antes da conclusão. A implementação
usa regras e a biblioteca padrão do Python, com testes automatizados para os
principais fluxos e casos de erro.

## Limites que devem acompanhar a apresentação

- O nome do projeto indica a direção de evolução; a versão atual não utiliza um modelo de IA.
- As regras reconhecem um conjunto limitado de palavras e expressões.
- Não há integração com WhatsApp, agenda, pagamentos ou cadastro de clientes.
- Os dados ficam na memória e são descartados ao concluir, cancelar ou encerrar.
- Confirmar o resumo não confirma disponibilidade nem reserva um horário.
- Ainda não existem medições de uso real ou ganhos de tempo comprovados.

Para executar os testes, use `python -m unittest -v`.
Consulte o [README](README.md) para as regras completas e limitações de datas.
