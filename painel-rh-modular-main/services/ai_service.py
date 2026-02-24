# services/ai_service.py
import google.generativeai as genai
from config.settings import AppConfig

def analisar_com_copiloto(dados_analise):
    """
    Envia os resultados do COPSOQ para a IA e retorna um parecer pericial.
    """
    if not AppConfig.GEMINI_API_KEY:
        return "Erro: Chave API não configurada no ficheiro .env ou Secrets."

    genai.configure(api_key=AppConfig.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    prompt_itajuba = f"""
    ATUE COMO: Consultor Sénior de Saúde Ocupacional e Perito em Riscos Psicossociais.
    CONTEXTO: Auxílio ao Psicólogo Marcos Bellini (CRP 04/37811) no Projeto Itajubá 2026.
    METODOLOGIA: COPSOQ III (Escala 0-100).
    
    OBJETIVO:
    Analise os seguintes dados e forneça um parecer técnico:
    1. Identifique os 2 maiores riscos (ex: Confiança Horizontal, Exigências).
    2. Explique o impacto desses riscos na gestão pública de Itajubá.
    3. Sugira 2 intervenções práticas imediatas.

    DADOS:
    {dados_analise}
    
    RESPOSTA: Use um tom profissional, direto e pericial.
    """
    
    try:
        response = model.generate_content(prompt_itajuba)
        return response.text
    except Exception as e:
        return f"Erro na análise da IA: {str(e)}"


