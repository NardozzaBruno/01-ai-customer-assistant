# AI Customer Assistant

A simple customer message classifier built with Python.

## About the Project

This project is the first step toward developing an AI-powered customer service assistant.

The current version uses keyword-based rules to identify customer service requests.

## Features

- Bath service classification
- Grooming service classification
- Combined bath and grooming classification
- General inquiry classification

## Technologies

- Python 3.12
- Git
- GitHub

## How to Run

Run the following command in the project folder:

`python main.py`

## Project Status

**Version 0.2:** Keyword-based message classifier with a reusable classification function and automated tests.

**Next steps:** Improve keyword matching and explore AI integration.
## Running Tests

Run `python -m unittest -v` in the project folder. No extra packages are required.

Tests cover service categories, uppercase messages, empty input, and terminal interaction.

## Current Limitations

Classification uses keyword fragments, so it can misinterpret negations or words containing those fragments. It does not yet understand customer intent.
