# Multi-Agent Document Intelligence System

## Project Overview
This project presents an advanced **Multi-Agent Document Intelligence System** designed to accurately classify, extract, and organize critical information from complex documents (e.g., Japanese solar construction records). By leveraging a collaborative architecture of specialized AI agents, the system achieves maximum accuracy and strict adherence to output contracts.

## Key Features
- **Multi-Agent Architecture**: Employs a modular and robust workflow containing specialized agents such as `TaskRouter`, `FileLocator`, `Planner`, `Extractor`, `Synthesizer`, `KeywordExtractor`, and `FileOrganizer`.
- **Intelligent Information Extraction**: High-precision extraction of relevant data utilizing evidence-anchored reasoning.
- **Dynamic File Organization**: Autonomous parsing, classification, and secure categorization of files into organized structures.

---

## Setup Instructions

**1. Install the `uv` Package Manager**
We use `uv` (an extremely fast Python package and project manager) to resolve and install dependencies seamlessly.
```bash
pip install uv
```

**2. Synchronize Dependencies**
Initialize the environment and sync all project dependencies:
```bash
uv sync
```

**3. Configure Environment Variables**
A template for environment variables is provided. Duplicate `.env.example` to create your active `.env` file:
```bash
cp .env.example .env
```

Open the `.env` file in your preferred text editor and securely populate the following required values:
- `COMPETITION_API_KEY`
- `BASE_URL`
- `OPENAI_API_KEY`

---

## Execution Instructions

To initialize the intelligent multi-agent pipeline and run the application, execute:
```bash
uv run python main.py
```
