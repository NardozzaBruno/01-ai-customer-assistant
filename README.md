# AI Customer Assistant

A simple customer message classifier built with Python.

## About the Project

This project is the first step toward developing an AI-powered customer service assistant.
The current version uses rules to classify Portuguese customer messages.

## Features

- Bath service classification
- Grooming service classification
- Combined bath and grooming classification
- General inquiry classification
- Whole-word matching, ignoring case and accents
- Simple negation handling with `nao`, `sem`, and `nem`

## Technologies

- Python 3.12
- Git
- GitHub

## How to Run

Run `python main.py` in the project folder and enter a message in Portuguese.

## Examples

| Message | Category |
| --- | --- |
| Quero banho e tosa | Banho e Tosa |
| Nao quero banho, so tosa | Tosa |
| Quero banho sem tosa | Banho |
| Nao quero banho nem tosa | Atendimento geral |
| A comida estava gostosa | Atendimento geral |

## Running Tests

Run `python -m unittest -v` in the project folder. No extra packages are required.
Tests cover service categories, uppercase and accented messages, empty input,
whole words, simple negations, request corrections, and terminal interaction.

## Project Status

**Version 0.3:** Whole-word matching and simple negation rules with automated tests.

**Next steps:** Expand language coverage and explore AI integration.

## Current Limitations

This is a rule-based prototype, not an AI language model. A negation applies to
following services until punctuation or a contrast/restriction word such as
`mas`, `porem`, `so`, `somente`, or `apenas`. The last mention of each service wins.

Complex sentences can still be misclassified, including `nao apenas banho, mas
tambem tosa`, `nao sei quanto custa o banho`, and `nao quero banho e quero tosa`.
Synonyms, plural forms, and spelling mistakes are not yet supported. When no
service is accepted, the result is `Atendimento geral`.
