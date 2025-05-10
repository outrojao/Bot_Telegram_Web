"""
Módulo para gerenciamento de sessões do Bot Telegram

Este módulo fornece:
- Registro e recuperação de logs de sessão
- Criptografia e descriptografia de arquivos de sessão
- Geração de nomes seguros para sessões
- Verificação de integridade de arquivos de sessão
"""

from .logger import (
    log_session,
    get_session,
)

from .manager import (
    encrypt_and_hash_session,
    get_session_path,
    save_session,
    get_saved_session,
)

__all__ = [
    # Funções do logger
    'log_session',
    'get_session',
    
    # Funções do manager
    'encrypt_and_hash_session',
    'get_session_path',
    'save_session',
    'get_saved_session',
]