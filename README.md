# Orin — AI Email Intelligence Engine

> Intelligent email outreach for e-commerce brands. NLP-powered lead scoring and personalized sequence generation.

## Overview

Orin is the core intelligence engine behind ParisAI Labs. It processes prospect data through a multi-stage NLP pipeline to identify high-intent leads and generate personalized email sequences.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Data Source  │────▶│ Score Engine │────▶│ Sequence Builder │
│ (Shopify/CSV)│     │ (Bedrock NLP)│     │ (Personalization)│
└─────────────┘     └──────────────┘     └─────────────────┘
                                                   │
                          ┌────────────────────────┘
                          ▼
                    ┌─────────────┐     ┌──────────────┐
                    │  SES Sender │────▶│  Analytics   │
                    │ (Throttled) │     │ (Conversion) │
                    └─────────────┘     └──────────────┘
```

## Key Metrics

- **15K+** emails processed
- **3.6%** cold prospect → interested lead conversion
- **99.2%** deliverability rate
- **<1.8s** average scoring latency

## Tech Stack

- Python 3.12
- AWS Bedrock (Claude, Titan Embeddings)
- Amazon SES (delivery)
- AWS Lambda (serverless processing)
- DynamoDB (prospect state)
- PostgreSQL (analytics)

## Project Structure

```
orin/
├── ingestion/          # Data source connectors (Shopify, CSV, API)
├── scoring/            # NLP lead scoring pipeline
├── generation/         # Email sequence generation
├── delivery/           # SES integration + throttling
├── analytics/          # Conversion tracking + reporting
└── tests/              # Unit + integration tests
```

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # Add your AWS credentials
python -m orin.cli score --input prospects.csv
python -m orin.cli generate --segment high-intent
```

## Configuration

See `.env.example` for required environment variables. Minimum: AWS credentials with Bedrock + SES access.

## License

Proprietary — ParisAI Labs SAS, 2025. All rights reserved.
