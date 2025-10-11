# test_all_validators.py
"""Testa os dois sistemas de validação juntos"""

from datetime import date
from utils.validators import DataValidator
from utils.file_validators import FileValidator
import io

print("=" * 50)
print("TESTE 1: DataValidator (regras de negócio)")
print("=" * 50)

# Teste datas
valid, msg = DataValidator.validate_date_range(date(2025, 1, 1), date(2025, 12, 31))
print(f"Datas válidas: {valid}")

valid, msg = DataValidator.validate_date_range(date(2025, 12, 31), date(2025, 1, 1))
print(f"Datas invertidas: {valid} - {msg}")

# Teste colaboradores
valid, msg = DataValidator.validate_employee_count(100)
print(f"100 colaboradores: {valid}")

valid, msg = DataValidator.validate_employee_count(-5)
print(f"-5 colaboradores: {valid} - {msg}")

# Teste validação múltipla
validations = [
    DataValidator.validate_date_range(date(2025, 1, 1), date(2025, 3, 1)),
    DataValidator.validate_employee_count(50),
    DataValidator.validate_percentage(15.5)
]
all_valid, errors = DataValidator.validate_all(validations)
print(f"\nValidação múltipla: {all_valid}")
if errors:
    for err in errors:
        print(f"  - {err}")

print("\n" + "=" * 50)
print("TESTE 2: FileValidator (já existente)")
print("=" * 50)

# Simula um CSV simples
csv_data = """nome,idade,salario
João,30,5000
Maria,25,4500
Pedro,35,6000"""

class FakeUploadedFile:
    def __init__(self, content, name):
        self.content = content.encode()
        self.name = name
        self.pos = 0
    
    def seek(self, pos):
        self.pos = pos
    
    def getvalue(self):
        return self.content

fake_file = FakeUploadedFile(csv_data, "teste.csv")
df, warnings, errors = FileValidator.read_file_robust(fake_file)

print(f"DataFrame lido: {df is not None}")
if df is not None:
    print(f"Linhas: {len(df)}, Colunas: {df.shape[1]}")
    print(f"Avisos: {warnings}")
    print(f"Erros: {errors}")

print("\nAmbos os validadores funcionando!")