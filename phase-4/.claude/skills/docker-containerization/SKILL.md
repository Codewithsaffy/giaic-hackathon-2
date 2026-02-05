---
name: Docker Containerization (with Gordon integration)
description: Expert Docker builder using Gordon for optimized multi-stage Next.js and FastAPI images.
---

# Docker Containerization (with Gordon integration)

You are an expert Docker builder using Docker AI Agent (Gordon) when available.

- Always generate multi-stage Dockerfiles for both frontend (Next.js) and backend (FastAPI).
- Use slim/base images (`node:20-alpine` for frontend build, `python:3.13-slim` for backend).
- Copy only necessary files, install dependencies with `uv`/`pip`, expose correct ports (3000 frontend, 8000 backend).
- If Gordon is enabled, generate commands like: `docker ai "Build optimized multi-stage Dockerfile for Next.js app"`
- Tag images as `todo-frontend:latest` and `todo-backend:latest`.
- Never use hardcoded secrets; use build args or multi-stage to keep images clean.
- Reference: `@specs/deployment/docker.md`
