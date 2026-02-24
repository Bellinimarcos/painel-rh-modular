# services/conversation_memory.py
"""
Sistema de memória persistente para conversações com IA.
Salva histórico entre sessões e permite busca contextual.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Gerencia histórico de conversações com persistência em disco"""
    
    def __init__(self, user_id: str = "default", storage_dir: str = "data/conversations"):
        self.user_id = user_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.current_file = self.storage_dir / f"{user_id}_history.json"
        self.messages = self._load()
        self.max_messages = 100  # Limite de mensagens armazenadas
    
    def _load(self) -> List[Dict]:
        """Carrega histórico do disco"""
        if self.current_file.exists():
            try:
                with open(self.current_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Histórico carregado: {len(data)} mensagens")
                return data
            except Exception as e:
                logger.error(f"Erro ao carregar histórico: {e}")
                return []
        return []
    
    def _save(self):
        """Salva histórico no disco"""
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
            logger.debug(f"Histórico salvo: {len(self.messages)} mensagens")
        except Exception as e:
            logger.error(f"Erro ao salvar histórico: {e}")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Adiciona mensagem ao histórico.
        
        Args:
            role: 'user' ou 'assistant'
            content: Conteúdo da mensagem
            metadata: Dados adicionais (ex: análise relacionada)
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.messages.append(message)
        
        # Mantém apenas últimas N mensagens
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        self._save()
    
    def get_recent_context(self, n: int = 6) -> str:
        """
        Retorna contexto das últimas N mensagens formatado.
        
        Args:
            n: Número de mensagens a incluir
        
        Returns:
            String formatada com o histórico
        """
        recent = self.messages[-n:] if len(self.messages) >= n else self.messages
        
        if not recent:
            return "Nenhum histórico anterior."
        
        context_lines = []
        for msg in recent:
            role_label = "Usuário" if msg['role'] == 'user' else "Assistente"
            # Trunca mensagens muito longas
            content = msg['content'][:500] + "..." if len(msg['content']) > 500 else msg['content']
            context_lines.append(f"{role_label}: {content}")
        
        return "\n".join(context_lines)
    
    def search_by_keyword(self, keyword: str, limit: int = 5) -> List[Dict]:
        """
        Busca mensagens que contêm palavra-chave.
        
        Args:
            keyword: Termo a buscar
            limit: Número máximo de resultados
        
        Returns:
            Lista de mensagens encontradas
        """
        keyword_lower = keyword.lower()
        results = [
            msg for msg in self.messages 
            if keyword_lower in msg['content'].lower()
        ]
        return results[-limit:] if len(results) > limit else results
    
    def get_messages_by_date(self, date_str: str) -> List[Dict]:
        """
        Retorna mensagens de uma data específica.
        
        Args:
            date_str: Data no formato 'YYYY-MM-DD'
        
        Returns:
            Lista de mensagens dessa data
        """
        return [
            msg for msg in self.messages 
            if msg['timestamp'].startswith(date_str)
        ]
    
    def get_context_for_analysis(self, analysis_id: str) -> str:
        """
        Retorna contexto de conversas sobre uma análise específica.
        
        Args:
            analysis_id: ID da análise
        
        Returns:
            Histórico relacionado formatado
        """
        related = [
            msg for msg in self.messages
            if msg.get('metadata', {}).get('analysis_id') == analysis_id
        ]
        
        if not related:
            return "Nenhuma conversa anterior sobre esta análise."
        
        lines = []
        for msg in related[-10:]:  # Últimas 10 mensagens relacionadas
            role = "Você" if msg['role'] == 'user' else "IA"
            lines.append(f"{role}: {msg['content'][:300]}")
        
        return "\n".join(lines)
    
    def clear(self):
        """Limpa todo o histórico"""
        self.messages = []
        self._save()
        logger.info("Histórico limpo")
    
    def export_conversation(self, output_file: Optional[str] = None) -> str:
        """
        Exporta conversa para arquivo de texto.
        
        Args:
            output_file: Caminho do arquivo de saída (opcional)
        
        Returns:
            Caminho do arquivo criado
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.storage_dir / f"export_{self.user_id}_{timestamp}.txt"
        
        output_path = Path(output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Conversa do usuário: {self.user_id}\n")
            f.write(f"Exportado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            for msg in self.messages:
                role = "USUÁRIO" if msg['role'] == 'user' else "ASSISTENTE"
                timestamp = msg['timestamp'][:19]  # Remove microsegundos
                f.write(f"[{timestamp}] {role}:\n")
                f.write(f"{msg['content']}\n\n")
                f.write("-" * 80 + "\n\n")
        
        logger.info(f"Conversa exportada para: {output_path}")
        return str(output_path)
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas sobre o histórico"""
        if not self.messages:
            return {"total_messages": 0}
        
        user_msgs = sum(1 for m in self.messages if m['role'] == 'user')
        assistant_msgs = sum(1 for m in self.messages if m['role'] == 'assistant')
        
        timestamps = [datetime.fromisoformat(m['timestamp']) for m in self.messages]
        first_msg = min(timestamps)
        last_msg = max(timestamps)
        
        return {
            "total_messages": len(self.messages),
            "user_messages": user_msgs,
            "assistant_messages": assistant_msgs,
            "first_message": first_msg.strftime("%Y-%m-%d %H:%M"),
            "last_message": last_msg.strftime("%Y-%m-%d %H:%M"),
            "days_active": (last_msg - first_msg).days + 1
        }