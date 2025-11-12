import os
import re

# Caminho da pasta principal
caminho = r"C:\Users\melissa.lemes\OneDrive - HITSS DO BRASIL SERVIÇOS TECNOLOGICOS LTDA\Área de Trabalho\umasopasta\beneficios\setembro25"
# Regex pra detectar CPF (com ou sem pontuação)
cpf_regex = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")

for nome in os.listdir(caminho):
    caminho_antigo = os.path.join(caminho, nome)

    if os.path.isdir(caminho_antigo) and " - " in nome:
        partes = nome.split(" - ")
        possivel_cpf = partes[-1].strip()

        # Se a última parte parece um CPF, renomeia pra só o CPF
        if cpf_regex.fullmatch(possivel_cpf):
            novo_nome = possivel_cpf.replace(".", "").replace("-", "")
            caminho_novo = os.path.join(caminho, novo_nome)
            os.rename(caminho_antigo, caminho_novo)
            print(f"✅ {nome} -> {novo_nome}")
        else:
            print(f"⏭️ Ignorado: {nome} (não parece CPF)")
