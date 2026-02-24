# C:\painel_rh_modular\models\copsoq_ii_model.py

from pydantic import BaseModel, Field
from typing import Optional

class CopsoqII(BaseModel):
    """
    Modelo de dados para as respostas do COPSOQ II - Versão Curta
    Baseado na adaptação de Magalhães, A. et al., 2024
    """
    
    # Critério: exigências laborais/organização do trabalho e conteúdo
    q1: Optional[int] = Field(None, description="1. A sua carga de trabalho acumula-se por ser mal distribuída?")
    q2: Optional[int] = Field(None, description="2. Com que frequência não tem tempo para completar todas as tarefas do seu trabalho?")
    q3: Optional[int] = Field(None, description="3. Precisa trabalhar muito rapidamente?")
    q4: Optional[int] = Field(None, description="4. O seu trabalho exige a sua atenção constante?")
    q5: Optional[int] = Field(None, description="5. O seu trabalho exige que tome decisões difíceis?")
    q6: Optional[int] = Field(None, description="6. O seu trabalho exige emocionalmente de si?")
    q7: Optional[int] = Field(None, description="7. Tem um elevado grau de influência no seu trabalho?")
    q8: Optional[int] = Field(None, description="8. O seu trabalho exige que tenha iniciativa?")
    q9: Optional[int] = Field(None, description="9. O seu trabalho permite-lhe aprender coisas novas?")
    q10: Optional[int] = Field(None, description="10. No seu local de trabalho, é informado com antecedência sobre decisões importantes, mudanças ou planos para o futuro?")
    q11: Optional[int] = Field(None, description="11. Recebe toda a informação de que necessita para fazer bem o seu trabalho?")
    q12: Optional[int] = Field(None, description="12. Sabe exatamente quais as suas responsabilidades?")
    q13: Optional[int] = Field(None, description="13. O seu trabalho é reconhecido e apreciado pela gerência?")
    q14: Optional[int] = Field(None, description="14. É tratado de forma justa no seu local de trabalho?")
    q15: Optional[int] = Field(None, description="15. Com que frequência tem ajuda e apoio do seu superior imediato?")
    q16: Optional[int] = Field(None, description="16. Existe um bom ambiente de trabalho entre si e os seus colegas?")
    
    # Critério: relações sociais e liderança
    q17: Optional[int] = Field(None, description="17. Oferece aos indivíduos e ao grupo boas oportunidades de desenvolvimento?")
    q18: Optional[int] = Field(None, description="18. É bom no planejamento do trabalho?")
    q19: Optional[int] = Field(None, description="19. A gerência confia nos seus funcionários para fazerem o seu trabalho bem?")
    q20: Optional[int] = Field(None, description="20. Confia na informação que lhe é transmitida pela gerência?")
    q21: Optional[int] = Field(None, description="21. Os conflitos são resolvidos de uma forma justa?")
    q22: Optional[int] = Field(None, description="22. O trabalho é igualmente distribuído pelos funcionários?")
    q23: Optional[int] = Field(None, description="23. Sou sempre capaz de resolver problemas, se tentar o suficiente.")
    
    # Critério: interface trabalho-indivíduo
    q24: Optional[int] = Field(None, description="24. O seu trabalho tem algum significado para si?")
    q25: Optional[int] = Field(None, description="25. Sente que o seu trabalho é importante?")
    q26: Optional[int] = Field(None, description="26. Sente que os problemas do seu local de trabalho são seus também?")
    q27: Optional[int] = Field(None, description="27. Quão satisfeito está com o seu trabalho de uma forma global?")
    q28: Optional[int] = Field(None, description="28. Sente-se preocupado em ficar desempregado?")
    
    # Critério: saúde geral
    q29: Optional[str] = Field(None, description="29. Em geral, sente que a sua saúde é:") # Resposta nominal
    
    # Critério: conflito trabalho/família
    q30: Optional[int] = Field(None, description="30. Sente que o seu trabalho lhe exige muita energia que acaba por afetar a sua vida privada negativamente?")
    q31: Optional[int] = Field(None, description="31. Sente que o seu trabalho lhe exige muito tempo que acaba por afetar a sua vida privada negativamente?")
    
    # Critério: saúde e bem-estar
    q32: Optional[int] = Field(None, description="32. Acordou várias vezes durante a noite e depois não conseguia adormecer novamente?")
    q33: Optional[int] = Field(None, description="33. Fisicamente exausto?")
    q34: Optional[int] = Field(None, description="34. Emocionalmente exausto?")
    q35: Optional[int] = Field(None, description="35. Irritado?")
    q36: Optional[int] = Field(None, description="36. Ansioso?")
    q37: Optional[int] = Field(None, description="37. Triste?")
    
    # Critério: comportamentos ofensivos
    q38: Optional[int] = Field(None, description="38. Tem sido alvo de insultos ou provocações verbais?")
    q39: Optional[int] = Field(None, description="39. Tem sido exposto a assédio sexual indesejado?")
    q40: Optional[int] = Field(None, description="40. Tem sido exposto a ameaças de violência?")
    q41: Optional[int] = Field(None, description="41. Tem sido exposto a violência física?")