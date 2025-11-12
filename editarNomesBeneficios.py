import os
import shutil
import pandas as pd
from datetime import datetime

# --- Caminhos ---
colab = r"C:\Users\melissa.lemes\OneDrive - HITSS DO BRASIL SERVIÇOS TECNOLOGICOS LTDA\Área de Trabalho\umasopasta\beneficios\setembro25"
caminhoExcel = r"C:\Users\melissa.lemes\OneDrive - HITSS DO BRASIL SERVIÇOS TECNOLOGICOS LTDA\Área de Trabalho\umasopasta\beneficios25.xlsx"
caminho_planilhas = r"C:\Users\melissa.lemes\OneDrive - HITSS DO BRASIL SERVIÇOS TECNOLOGICOS LTDA\Área de Trabalho\umasopasta\planilhasIDCPF"

# =============================================================
# ETAPA 1 + 2 - Coleta nomes, junta com planilhas e atualiza CPFs
# =============================================================

dfs_ref = []
for arquivo in os.listdir(caminho_planilhas):
    if arquivo.endswith(".xlsx"):
        caminho_arquivo = os.path.join(caminho_planilhas, arquivo)
        df_temp = pd.read_excel(caminho_arquivo, dtype=str)
        colunas = [c.strip().upper().replace(" ", "_") for c in df_temp.columns]
        df_temp.columns = colunas

        col_id = next((c for c in colunas if "ID" in c and "VAGA" in c), None)
        col_cpf = next((c for c in colunas if "CPF" in c), None)
        col_nome = next((c for c in colunas if "NOME" in c), None)

        if col_id and col_cpf:
            colunas_para_pegar = {col_id: "Id da vaga", col_cpf: "CPF"}
            if col_nome:
                colunas_para_pegar[col_nome] = "Nome completo"
            df_filtrado = df_temp[list(colunas_para_pegar.keys())].rename(columns=colunas_para_pegar)
            dfs_ref.append(df_filtrado)

if dfs_ref:
    df_ref = pd.concat(dfs_ref, ignore_index=True).drop_duplicates(subset=["Id da vaga"])
    df_ref["Id da vaga"] = df_ref["Id da vaga"].astype(str).str.strip()
    df_ref["CPF"] = df_ref["CPF"].astype(str).str.strip()
else:
    df_ref = pd.DataFrame(columns=["Id da vaga", "CPF", "Nome completo"])

# --- Se o Excel ainda não existir, cria uma nova tabela chamada "benefícios 2025"
if not os.path.exists(caminhoExcel):
    print("📘 Criando nova planilha 'benefícios 2025'...")
    df_principal = pd.DataFrame(columns=["Nome", "Id da vaga", "NOME_PASTA", "CPF", "Nome completo"])
    df_principal.to_excel(caminhoExcel, index=False)
else:
    df_principal = pd.read_excel(caminhoExcel, dtype=str)

# --- Coleta nomes das pastas ---
pastas = [nome for nome in os.listdir(colab) if os.path.isdir(os.path.join(colab, nome))]
dados = []
for p in pastas:
    partes = p.split(" - ")
    if len(partes) >= 2:
        nome, id_vaga = partes[0], partes[1]
    else:
        nome, id_vaga = p, ""
    dados.append({
        "Nome": nome.strip(),
        "Id da vaga": id_vaga.strip(),
        "NOME_PASTA": p,
    })

df_novo = pd.DataFrame(dados)

if not df_principal.empty:
    df_final = pd.concat([df_principal, df_novo], ignore_index=True)
    df_final = df_final.drop_duplicates(subset=["NOME_PASTA"]).reset_index(drop=True)
else:
    df_final = df_novo.copy()

df_final["Id da vaga"] = df_final["Id da vaga"].astype(str).str.strip()
df_ref["Id da vaga"] = df_ref["Id da vaga"].astype(str).str.strip()
df_merge = df_final.merge(df_ref, on="Id da vaga", how="left", suffixes=("", "_novo"))

for coluna in ["CPF", "Nome completo"]:
    if coluna in df_merge.columns and f"{coluna}_novo" in df_merge.columns:
        df_merge[coluna] = df_merge[coluna].fillna(df_merge[f"{coluna}_novo"])
        df_merge.drop(columns=[f"{coluna}_novo"], inplace=True)

# --- Limpa valores "nan" e "None" ---
for c in ["CPF", "Nome completo"]:
    if c in df_merge.columns:
        df_merge[c] = df_merge[c].replace(["nan", "NaN", "None"], "").fillna("")

df_final = df_merge
df_final.to_excel(caminhoExcel, index=False)

print(f"✅ Planilha 'benefícios 2025' atualizada com sucesso! Total de registros: {len(df_final)}")

# =============================================================
# ETAPA 3 - Renomeia pastas com nome abreviado + CPF
# =============================================================

def abreviar_nome(nome_completo: str) -> str:
    """Retorna o primeiro nome e o primeiro sobrenome, ignorando preposições."""
    if not nome_completo:
        return ""
    
    partes = nome_completo.strip().split()
    if len(partes) == 1:
        return partes[0]

    preposicoes = {"da", "de", "do", "das", "dos", "e"}
    primeiro_nome = partes[0]
    sobrenome = ""

    # Encontra o primeiro sobrenome que não seja preposição
    for p in partes[1:]:
        if p.lower() not in preposicoes:
            sobrenome = p
            break

    if not sobrenome:  # caso todos sejam preposições (raro)
        return primeiro_nome

    return f"{primeiro_nome} {sobrenome}"

def encurtar_nome(nome, limite=100):
    if len(nome) > limite:
        nome = nome[:limite - 3] + "..."
    return nome

print("\n🚀 Iniciando renomeação das pastas...")

for _, linha in df_final.iterrows():
    nome_pasta_antiga = linha.get("NOME_PASTA", "")
    nome_completo = linha.get("Nome completo", "") or linha.get("Nome", "")
    cpf = linha.get("CPF", "")

    if pd.isna(cpf) or str(cpf).strip() in ["", "nan", "none"]:
        print(f"⚠️ Sem CPF para {nome_pasta_antiga}, mantendo nome original.")
        continue

    pasta_antiga = os.path.join(colab, nome_pasta_antiga)
    if not os.path.exists(pasta_antiga):
        continue

    nome_abreviado = abreviar_nome(nome_completo)
    nova_pasta_nome = encurtar_nome(f"{nome_abreviado} - {cpf}")
    pasta_nova = os.path.join(colab, nova_pasta_nome)

    if os.path.exists(pasta_nova):
        print(f"⚠️ Já existe pasta com nome {nova_pasta_nome}, pulando...")
        continue

    try:
        os.rename(pasta_antiga, pasta_nova)
        print(f"✅ {nome_pasta_antiga} ➜ {nova_pasta_nome}")
        df_final.loc[df_final["NOME_PASTA"] == nome_pasta_antiga, "NOME_PASTA"] = nova_pasta_nome
    except Exception as e:
        print(f"❌ Erro ao renomear {nome_pasta_antiga}: {e}")

df_final.to_excel(caminhoExcel, index=False)
print("\n🏁 Renomeação concluída com sucesso!")
