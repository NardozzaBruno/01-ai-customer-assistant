# AI Customer Assistant

A Python prototype that turns a pet-shop service request into a reviewable summary
of the service, pet size, and preferred date.

## Problem and Approach

Before a bath or grooming request can be reviewed, the pet shop needs basic details.
This project demonstrates how a conversation can collect those details, remember
previous answers, validate dates, and let the customer correct the result.

The current implementation uses deterministic rules, not an AI model. It runs locally
without paid APIs and does not connect to a booking system. The project name reflects
its intended direction; the implemented behavior is described below.

**Try the [guided demonstration](DEMO.md)** for a two-minute walkthrough, real example
replies, extra scenarios, and a short Portuguese portfolio description.

## Quick Start

With Python 3.12 and Git installed, open a terminal in the directory where you want
to keep the project:

```powershell
git clone https://github.com/NardozzaBruno/01-ai-customer-assistant.git
cd 01-ai-customer-assistant
python main.py
```

If you already have the project locally, open its folder in a terminal and run
`python main.py`. No additional packages, API keys, or account setup are needed.

Try `quero banho para um pet grande amanha`, review the summary, then type
`confirmar` to complete the demonstration request or `sair` to exit.

## Implementation Highlights

- Stateful conversation with collection, review, correction, and reset behavior
- Whole-word matching, accent normalization, and simple negation handling
- Calendar validation and an injectable clock for reproducible date tests
- Automated tests for normal conversations, invalid input, and session boundaries

The prototype demonstrates these behaviors; it has not been evaluated with real
customers, and no business-performance claims are made.

## Features

- Classifies bath, grooming, combined services, and general inquiries
- Matches whole words, ignoring case and accents
- Handles simple negations such as `nao quero banho, so tosa`
- Remembers the selected service, pet size, and preferred day during a request
- Extracts size and day from natural phrases and combined service requests
- Asks only for missing details and requests clarification for ambiguous details
- Resolves relative days, weekdays, and numeric dates to calendar dates
- Rejects invalid dates and past days without overwriting the previous request
- Displays a dated request summary for customer review
- Allows service, size, and date corrections before explicit `confirmar`
- Concludes only the demonstration request; never confirms a real booking
- Supports `cancelar` or `reiniciar` to discard a request, and `sair` to exit

## Technologies

- Python 3.12
- Git and GitHub
- Python standard library only; no additional packages or AI API required

## How to Run

Run `python main.py` in the project folder.

1. Enter the service, for example `quero banho`.
2. Reply with `pequeno`, `medio`, or `grande` for the pet size.
3. Reply with `hoje`, `amanha`, a weekday such as `sexta-feira`, or a date such as `28/10/2026`.
4. Review the summary. Correct the service, size, or date by entering its new value.
5. Type `confirmar` to conclude the demonstration request, or `cancelar` to discard it.

Availability must still be checked by the pet shop. Nothing is sent to the pet shop.

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

See the [guided demonstration](DEMO.md#exemplo-real-das-respostas) for a complete
conversation, including a size correction and explicit completion.

## Date Rules

- The current day is read in America/Sao_Paulo. If the IANA timezone database is
  unavailable on Windows, the clock falls back to Sao Paulo's current UTC-3 offset.
- `hoje`, `amanha`, and `depois de amanha` resolve to today, tomorrow, and two days ahead.
- A weekday means its next occurrence, including today when it matches.
- Dates accept `D/M`, `DD/MM`, or a four-digit year, such as `28/10/2026`.
- Omitting the year means the current year. Past dates are rejected, without silently
  rolling them forward to next year. Supply the year for a future-year request.
- Invalid calendar dates, past dates, and `ontem`/`anteontem` are rejected.
- Multiple date expressions require clarification, even if they could mean the same day.
- An invalid date leaves all previous details intact. A stored date that becomes past
  while the program remains open must be replaced before a summary can be produced.

## Session Behavior

- `cancelar` and `reiniciar` discard all details of the current request.
- During initial collection, changing the service clears old details.
- During review, changing the service preserves the size and date; other supplied
  details update their respective fields.
- Repeating the same service preserves previously collected details.
- A new unambiguous size or day replaces that detail and displays an updated summary
  whenever all required fields are present. Invalid input preserves the request.
- Displaying a summary keeps the request in memory for review.
- Only the standalone command `confirmar` concludes a complete, current request.
  `sim`, `ok`, and messages containing additional text do not conclude it.
- Confirmation, cancellation, or restart clears the request for the next customer.
- Exiting discards the session. If a date expires before confirmation, a new date
  is required; the service and size are preserved.
- Data is kept only in memory. Nothing is saved to disk or sent to a booking system.

## Running Tests

Run `python -m unittest -v` in the project folder.
Tests cover classification, simple negations, replies, full terminal conversations,
size/day order, invalid details, cancellation, service changes, independent sessions,
exit commands, end-of-input, natural phrases, combined details, corrections,
repeated services, ambiguous details, whole-word detail matching, numeric dates,
relative days, weekdays, leap years, year boundaries, past dates, timezone conversion,
summary corrections, explicit confirmation, cancellation during review, expired-date
confirmation, and reset between customers.

## Project Status

**Version 0.9:** Reviewable summaries, corrections, and explicit request completion.

**Portfolio walkthrough:** See [DEMO.md](DEMO.md).

**Next steps:** Collect feedback from manual demonstrations before choosing the next feature.

## Current Limitations

This is a rule-based prototype, not an AI language model or a real booking system.
Extraction uses whole-word keywords: `pequeno`, `medio`, `grande`, `hoje`,
`amanha`, and weekday names. It does not understand arbitrary language, sarcasm,
or whether an unrelated mention actually describes this pet or request.
Month names, times, synonyms, and multiple pets are not yet supported.
Negated details are handled conservatively by asking for clarification, even
when a human could infer the intended answer.
Calendar dates are preferences only; availability is not checked. No appointment,
price, or time slot is confirmed. More complex relative expressions such as
`daqui a duas semanas` are not supported. Weekday modifiers such as `proxima`
do not change the next-occurrence rule.

A negation applies to following services until punctuation or a word such as
`mas`, `porem`, `so`, `somente`, or `apenas`. The last mention of each service wins.
Complex sentences such as `nao apenas banho, mas tambem tosa`,
`nao sei quanto custa o banho`, and `nao quero banho e quero tosa` can still be
misclassified. Synonyms, plural forms, and spelling mistakes are not supported.

## Project Files

| File | Purpose |
| --- | --- |
| `main.py` | Classification, date handling, conversation state, and terminal interaction |
| `test_main.py` | Automated tests |
| `DEMO.md` | Guided presentation and portfolio description |

## Contributing

Reproduce a problem with a short conversation and include the expected result.
For behavior changes, add a relevant test and run `python -m unittest -v`.
Keep examples and documented limitations consistent with the actual implementation.
