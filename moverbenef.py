import os
import shutil

# Caminhos principais
caminho_beneficios = r"C:Área de Trabalho\umasopasta\beneficios\setembro25"
caminho_funcionarios = r"C:Área de Trabalho\umasopasta\funcionarios\setembro25"

# Listar pastas de benefícios (CPFs)
pastas_beneficios = [p for p in os.listdir(caminho_beneficios) if os.path.isdir(os.path.join(caminho_beneficios, p))]

total_movidos = 0
sem_destino = []

print("🚀 Iniciando movimentação de arquivos...\n")

for cpf in pastas_beneficios:
    pasta_origem = os.path.join(caminho_beneficios, cpf)
    pasta_destino = os.path.join(caminho_funcionarios, cpf)

    if not os.path.exists(pasta_destino):
        print(f"⚠️ Funcionário com CPF {cpf} não encontrado em setembro, pulando...")
        sem_destino.append(cpf)
        continue

    # Mover todos os arquivos e subpastas
    for item in os.listdir(pasta_origem):
        origem = os.path.join(pasta_origem, item)
        destino = os.path.join(pasta_destino, item)

        # Evita sobrescrever arquivos existentes
        if os.path.exists(destino):
            print(f"⚠️ Arquivo já existe: {destino}, pulando...")
            continue

        try:
            shutil.move(origem, destino)
            total_movidos += 1
            print(f"✅ Movido: {origem} ➜ {destino}")
        except Exception as e:
            print(f"❌ Erro ao mover {origem}: {e}")

# Remover pastas vazias em benefícios
for cpf in pastas_beneficios:
    pasta_origem = os.path.join(caminho_beneficios, cpf)
    if os.path.isdir(pasta_origem) and not os.listdir(pasta_origem):
        os.rmdir(pasta_origem)
        print(f"🧹 Pasta vazia removida: {pasta_origem}")

print("\n🏁 Processo concluído!")
print(f"📦 Total de arquivos movidos: {total_movidos}")
print(f"🚫 Pastas sem destino correspondente: {len(sem_destino)}")
if sem_destino:
    print("   → " + ", ".join(sem_destino))
