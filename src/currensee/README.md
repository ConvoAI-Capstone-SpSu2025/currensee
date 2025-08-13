# CurrenSee Python Package

This directory contains the core Python package for the CurrenSee platform, a multi-agent AI system for financial advisory intelligence.

## Overview

The `currensee` package implements the main backend logic for CurrenSee, including:
- Multi-agent orchestration for data integration and report generation
- API endpoints (FastAPI)
- Core business logic and utilities
- Data schemas and validation
- Security guardrails

## Directory Structure

- `agents/`   — Specialized agent modules for data retrieval, summarization, and orchestration
- `api/`      — FastAPI application and route definitions
- `core/`     — Core logic, state management, and orchestration (e.g., LangGraph, supervisor state)
- `schema/`   — Pydantic models and data validation schemas
- `utils/`    — Utility functions and helpers
- `__init__.py` — Package initialization

## Key Features
- **Multi-Agent Orchestration:** 15+ specialized agents for CRM, Outlook, financial news, and more
- **Secure API:** FastAPI-based endpoints for report generation and feedback
- **Dynamic Learning:** User preference adaptation and feedback loops
- **Robust Guardrails:** Input/output validation for PII, compliance, and hallucination prevention

## Usage
This package is not intended to be run directly. Use the API server entrypoint in `currensee.api.main` (see the main project README for instructions).

## Contributing
See the root project README for development, testing, and contribution guidelines.

---

For more information, see the main [CurrenSee README](../../README.md).
