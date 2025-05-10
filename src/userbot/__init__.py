"""
Módulo para gerenciamento do UserBot com IA integrada

Este módulo fornece:
- Integração com a API do Telegram via Telethon
- Processamento de mensagens com modelo de IA (LiteLLM + OpenRouter)
- Gerenciamento de conversas com contexto por usuário
- Buffer inteligente para agrupamento de mensagens
- Histórico de conversas para manutenção de contexto

Principais funcionalidades:
- Inicialização assíncrona do userbot
- Processamento em tempo real de mensagens privadas
- Respostas contextualizadas usando histórico de conversa
- Prevenção de race conditions com sistema de locks por usuário
- Configuração flexível do modelo de IA via variáveis de ambiente

Dependências externas:
- LiteLLM: Para integração com modelos de IA
- Telethon: Para comunicação com a API do Telegram
- python-dotenv: Para gerenciamento de configurações

Variáveis de ambiente necessárias:
- OPENROUTER_API_KEY: Chave para autenticação no OpenRouter
- MODEL: Modelo de IA a ser utilizado (opcional)
"""

from .userbot import start_userbot

__all__ = [
    'start_userbot'
]