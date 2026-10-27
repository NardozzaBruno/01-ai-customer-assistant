# AI Customer Assistant

A rule-based Portuguese customer service prototype for a pet shop, built with Python.

## Features

- Classifies bath, grooming, combined services, and general inquiries
- Matches whole words, ignoring case and accents
- Handles simple negations such as `nao quero banho, so tosa`
- Remembers the selected service, pet size, and preferred day during a request
- Extracts size and day from natural phrases and combined service requests
- Asks only for missing details and requests clarification for ambiguous details
- Displays a request summary without confirming a booking
- Supports `cancelar` or `reiniciar` to discard a request, and `sair` to exit

## Technologies

- Python 3.12
- Git and GitHub
- Python standard library only; no additional packages or AI API required

## How to Run

Run `python main.py` in the project folder.

1. Enter the service, for example `quero banho`.
2. Reply with `pequeno`, `medio`, or `grande` for the pet size.
3. Reply with `hoje`, `amanha`, or a weekday such as `sexta-feira`.
4. Read the request summary. Availability must still be checked by the pet shop.

Accents and uppercase letters are accepted. Size and day can be supplied in either
order, separately or together. Examples:

- `Meu pet e pequeno.`
- `Pode ser amanha.`
- `Quero banho para um pet grande amanha.`
- `Ele e pequeno e pode ser na terca-feira.`

Recognized details are kept even if the service has not been selected yet.
The assistant asks only for missing details. Multiple sizes or days such as
`amanha ou sexta` require clarification and leave the previous request unchanged.
Simple negations near details also require clarification.
Empty input shows a hint. End-of-input or Ctrl+C ends the session gracefully.

## Conversation Example

```text
Cliente: quero banho
Assistente: Certo, banho! Qual é o porte do seu pet (pequeno, médio ou grande)?
Cliente: pequeno
Assistente: Para qual dia? Responda hoje, amanhã ou um dia da semana.
Cliente: amanhã
Assistente: Resumo da solicitação: Banho; porte pequeno; dia desejado: amanhã. Agendamento não confirmado: depende da disponibilidade do pet shop. Para iniciar outra solicitação, informe o serviço.
```

## Session Behavior

- `cancelar` and `reiniciar` discard all details of the current request.
- Changing the service clears old details and uses any details in the new message.
- Repeating the same service preserves previously collected details.
- A new unambiguous size or day replaces that detail before the summary is shown.
- After displaying a summary, the assistant clears the request for the next customer.
- Data is kept only in memory. Nothing is saved to disk or sent to a booking system.

## Running Tests

Run `python -m unittest -v` in the project folder.
Tests cover classification, simple negations, replies, full terminal conversations,
size/day order, invalid details, cancellation, service changes, independent sessions,
exit commands, end-of-input, natural phrases, combined details, corrections,
repeated services, ambiguous details, and whole-word detail matching.

## Project Status

**Version 0.7:** Natural phrases and combined details with clarification for ambiguity.

**Next steps:** Expand supported answers and date validation, then explore AI integration.

## Current Limitations

This is a rule-based prototype, not an AI language model or a real booking system.
Extraction uses whole-word keywords: `pequeno`, `medio`, `grande`, `hoje`,
`amanha`, and weekday names. It does not understand arbitrary language, sarcasm,
or whether an unrelated mention actually describes this pet or request.
Dates such as `28/10`, synonyms, and multiple pets are not yet supported.
Negated details are handled conservatively by asking for clarification, even
when a human could infer the intended answer.
Days are stored as preference labels, not resolved to calendar dates or checked
against availability. No appointment, price, or time slot is confirmed.

A negation applies to following services until punctuation or a word such as
`mas`, `porem`, `so`, `somente`, or `apenas`. The last mention of each service wins.
Complex sentences such as `nao apenas banho, mas tambem tosa`,
`nao sei quanto custa o banho`, and `nao quero banho e quero tosa` can still be
misclassified. Synonyms, plural forms, and spelling mistakes are not supported.
