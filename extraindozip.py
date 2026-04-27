import os
import zipfile
import shutil
import stat

##editar esse codigo para que quando ele for renomear, ele pegar a ultima palavra do nome dos arquivos de benefícios

# ---------------- CONFIGURAÇÕES ----------------
caminho_zips = r"C:\Área de Trabalho\umasopasta\funcionarios\arquivoszip"
pasta_destino = r"C:\Área de Trabalho\umasopasta\funcionarios\outubro25"

os.makedirs(pasta_destino, exist_ok=True)
MAX_PATH = 200  # limite total para o caminho no Windows

# ---------------- FUNÇÕES ----------------
def encurtar_nome_arquivo(caminho_func, nome_arquivo):
    base, ext = os.path.splitext(nome_arquivo)
    caminho_total = os.path.join(caminho_func, nome_arquivo)
    if len(caminho_total) <= MAX_PATH:
        return nome_arquivo
    excesso = len(caminho_total) - MAX_PATH
    base = base[:-excesso]
    return base + ext

def forcar_remocao(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"⚠️ Não foi possível forçar remoção de {path}: {e}")

def remover_pastas_vazias(caminho):
    for raiz, pastas, _ in os.walk(caminho, topdown=False):
        for pasta in pastas:
            caminho_pasta = os.path.join(raiz, pasta)
            try:
                if not os.listdir(caminho_pasta):
                    os.chmod(caminho_pasta, stat.S_IWRITE)
                    os.rmdir(caminho_pasta)
                    print(f"🗑️ Pasta vazia removida: {caminho_pasta}")
            except Exception as e:
                try:
                    shutil.rmtree(caminho_pasta, ignore_errors=False, onerror=forcar_remocao)
                    print(f"🗑️ Pasta bloqueada removida com força: {caminho_pasta}")
                except Exception as ex:
                    print(f"⚠️ Erro ao forçar remoção de {caminho_pasta}: {ex}")

def extrair_zip_funcionarios(zip_path, destino):
    print(f"\n➡️ Processando ZIP: {os.path.basename(zip_path)}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        pastas_funcionarios = set(item.split("/")[0] for item in zip_ref.namelist() if "/" in item)
        
        for func in pastas_funcionarios:
            caminho_func = os.path.join(destino, func)
            os.makedirs(caminho_func, exist_ok=True)
            print(f"  📂 Extraindo arquivos do funcionário: {func}")
            
            for item in zip_ref.namelist():
                if item.startswith(func + "/") and not item.endswith("/"):
                    nome_arquivo = os.path.basename(item)
                    nome_arquivo_original = nome_arquivo
                    nome_arquivo = encurtar_nome_arquivo(caminho_func, nome_arquivo)
                    caminho_arquivo = os.path.join(caminho_func, nome_arquivo)

                    # Renomeia se já existir
                    sufixo = 1
                    caminho_final = caminho_arquivo
                    while os.path.exists(caminho_final):
                        base, ext = os.path.splitext(nome_arquivo)
                        caminho_final = os.path.join(caminho_func, f"{base}_{sufixo}{ext}")
                        sufixo += 1
                    if caminho_final != caminho_arquivo:
                        print(f"    ⚠️ Arquivo duplicado encontrado. Renomeando para: {os.path.basename(caminho_final)}")
                    elif nome_arquivo != nome_arquivo_original:
                        print(f"    ⚠️ Nome muito longo. Encurtando para: {nome_arquivo}")

                    # Extrai arquivo
                    with zip_ref.open(item) as origem, open(caminho_final, "wb") as destino_arquivo:
                        shutil.copyfileobj(origem, destino_arquivo)
                    print(f"    ✅ Extraído: {os.path.basename(caminho_final)}")

# ---------------- REMOVE TODOS OS .TXT ----------------
def remover_txt(caminho_func):
    for raiz, _, arquivos in os.walk(caminho_func):
        for arquivo in arquivos:
            if arquivo.lower().endswith(".txt"):
                caminho_arquivo = os.path.join(raiz, arquivo)
                try:
                    os.chmod(caminho_arquivo, stat.S_IWRITE)
                    os.remove(caminho_arquivo)
                    print(f"🗑️ Arquivo .txt removido: {caminho_arquivo}")
                except Exception as e:
                    print(f"⚠️ Erro ao remover {caminho_arquivo}: {e}")

# ---------------- EXECUÇÃO ----------------
# Extrai todos os ZIPs
for arquivo in os.listdir(caminho_zips):
    if arquivo.lower().endswith(".zip"):
        extrair_zip_funcionarios(os.path.join(caminho_zips, arquivo), pasta_destino)

# Remove .txt de todos os funcionários
for funcionario in os.listdir(pasta_destino):
    caminho_func = os.path.join(pasta_destino, funcionario)
    if os.path.isdir(caminho_func):
        remover_txt(caminho_func)

# Remove pastas vazias
for funcionario in os.listdir(pasta_destino):
    caminho_func = os.path.join(pasta_destino, funcionario)
    if os.path.isdir(caminho_func):
        remover_pastas_vazias(caminho_func)

print("\n🎉 Todos os arquivos foram extraídos, arquivos .txt removidos e pastas vazias limpas!")
