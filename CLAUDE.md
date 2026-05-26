# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

API key is stored in `.env` and must not be committed to git (already in `.gitignore`).

```
OPENROUTER_API_KEY=...
```

Copy `.env.example` to `.env` when setting up a fresh clone.

## OpenRouter

This project uses [OpenRouter](https://openrouter.ai) as the LLM API gateway. Requests are made to `https://openrouter.ai/api/v1` using the key from `OPENROUTER_API_KEY`. The API is OpenAI-compatible, so standard OpenAI SDKs work by pointing `base_url` at OpenRouter.

OpenRouter API를 이용해서 실제 AI 모델이 이미지를 인식하고 관상 풀이를 생성하게 해줘. 매번 실행할 때마다 API가 정확히 작동했는지, AI모델이 문제없이 실행되었는지 파악하고, 문제가 있다면 어떤 문제가 있는지 보고해. 