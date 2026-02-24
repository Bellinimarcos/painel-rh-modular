# services/knowledge_base.py
"""
Base de conhecimento simples para armazenar documentos e políticas de RH.
Permite busca por palavras-chave sem dependências pesadas.
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SimpleKnowledgeBase:
    """Base de conhecimento sem dependências externas pesadas"""
    
    def __init__(self, storage_dir: str = "data/knowledge_base"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.kb_file = self.storage_dir / "documents.json"
        self.documents = self._load()
    
    def _load(self) -> List[Dict]:
        """Carrega documentos do disco"""
        if self.kb_file.exists():
            try:
                with open(self.kb_file, 'r', encoding='utf-8') as f:
                    docs = json.load(f)
                logger.info(f"Base de conhecimento carregada: {len(docs)} documentos")
                return docs
            except Exception as e:
                logger.error(f"Erro ao carregar base: {e}")
                return []
        return []
    
    def _save(self):
        """Salva documentos no disco"""
        try:
            with open(self.kb_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
            logger.debug(f"Base salva: {len(self.documents)} documentos")
        except Exception as e:
            logger.error(f"Erro ao salvar base: {e}")
    
    def add_document(
        self, 
        title: str, 
        content: str, 
        category: str = "geral",
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Adiciona documento à base.
        
        Args:
            title: Título do documento
            content: Conteúdo completo
            category: Categoria (ex: "política", "procedimento", "manual")
            tags: Tags para facilitar busca
        
        Returns:
            ID do documento criado
        """
        doc_id = f"doc_{len(self.documents) + 1}_{int(datetime.now().timestamp())}"
        
        document = {
            "id": doc_id,
            "title": title,
            "content": content,
            "category": category,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "word_count": len(content.split())
        }
        
        self.documents.append(document)
        self._save()
        
        logger.info(f"Documento adicionado: {title} ({doc_id})")
        return doc_id
    
    def search(self, query: str, top_k: int = 5, category: str = None):
        """Busca documentos por palavras-chave NO CONTEDO COMPLETO"""
        if not self.documents:
            return []
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        results = []
        
        for doc in self.documents:
            # Filtro por categoria
            if category and doc['category'] != category:
                continue
            
            # Busca em TÍTULO, TAGS E CONTEDO COMPLETO
            title_lower = doc['title'].lower()
            tags_lower = ' '.join(doc.get('tags', [])).lower()
            content_lower = doc['content'].lower()
            
            # Calcula score baseado em onde as palavras aparecem
            score = 0
            
            # Pontos para cada palavra encontrada
            for word in query_words:
                if word in title_lower:
                    score += 100  # Título tem mais peso
                if word in tags_lower:
                    score += 50   # Tags também
                score += content_lower.count(word) * 10  # Conteúdo completo
            
            if score > 0:
                # Encontra snippet relevante com MLTIPLOS trechos
                snippet = self._extract_snippet(doc['content'], query_words, max_length=2000)
                
                results.append({
                    'document': doc,
                    'score': score,
                    'snippet': snippet
                })
        
        # Ordena por relevância e retorna top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    def _extract_snippet(self, content: str, query_words: set, max_length: int = 2000):
        """Extrai MLTIPLOS trechos relevantes do conteúdo"""
        content_lower = content.lower()
        snippets = []
        positions = []
        
        # Encontra TODAS as ocorrências de qualquer palavra-chave
        for word in query_words:
            pos = 0
            while True:
                pos = content_lower.find(word, pos)
                if pos == -1:
                    break
                positions.append(pos)
                pos += 1
        
        if not positions:
            # Nenhuma palavra encontrada, retorna início
            return content[:max_length] + "..."
        
        # Remove duplicatas e ordena
        positions = sorted(set(positions))
        
        # Pega até 3 trechos diferentes (para não estourar o limite da API)
        max_snippets = 3
        snippet_size = 800  # Cada snippet com 800 caracteres
        
        used_ranges = []
        for pos in positions[:10]:  # Analisa até 10 ocorrências
            # Verifica se esta posição já está coberta
            already_covered = False
            for start, end in used_ranges:
                if start <= pos <= end:
                    already_covered = True
                    break
            
            if not already_covered and len(snippets) < max_snippets:
                # Extrai contexto ao redor
                start = max(0, pos - 200)
                end = min(len(content), pos + snippet_size - 200)
                
                snippet = content[start:end]
                
                # Adiciona reticências
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."
                
                snippets.append(snippet)
                used_ranges.append((start, end))
        
        # Junta os snippets
        return "\n\n[...]\n\n".join(snippets)
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Retorna todos documentos de uma categoria"""
        return [doc for doc in self.documents if doc['category'] == category]
    
    def get_by_id(self, doc_id: str) -> Optional[Dict]:
        """Busca documento por ID"""
        return next((doc for doc in self.documents if doc['id'] == doc_id), None)
    
    def delete_document(self, doc_id: str) -> bool:
        """Remove documento da base"""
        original_len = len(self.documents)
        self.documents = [doc for doc in self.documents if doc['id'] != doc_id]
        
        if len(self.documents) < original_len:
            self._save()
            logger.info(f"Documento removido: {doc_id}")
            return True
        return False
    
    def get_all_categories(self) -> List[str]:
        """Lista todas as categorias existentes"""
        return list(set(doc['category'] for doc in self.documents))
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas da base"""
        if not self.documents:
            return {"total_documents": 0}
        
        categories = {}
        total_words = 0
        
        for doc in self.documents:
            cat = doc['category']
            categories[cat] = categories.get(cat, 0) + 1
            total_words += doc.get('word_count', 0)
        
        return {
            "total_documents": len(self.documents),
            "categories": categories,
            "total_words": total_words,
            "avg_words_per_doc": total_words // len(self.documents) if self.documents else 0
        }
    
    def format_search_results(self, results: List[Dict]) -> str:
        """Formata resultados de busca para exibição"""
        if not results:
            return "Nenhum documento encontrado."
        
        formatted = []
        for i, result in enumerate(results, 1):
            doc = result['document']
            formatted.append(f"""
**{i}. {doc['title']}** (Categoria: {doc['category']})
Relevância: {result['score']} pontos
Trecho: {result['snippet']}
---""")
        
        return "\n".join(formatted)


