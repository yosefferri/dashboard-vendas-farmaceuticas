import csv
import random

# Nome do arquivo final
nome_arquivo = "dados_100k.csv"

# Definição das colunas
cabecalho = ["id", "nome", "idade", "valor"]

print("Gerando arquivo CSV com 100.000 linhas...")

with open(nome_arquivo, mode="w", newline="", encoding="utf-8") as arquivo:
    escritor = csv.writer(arquivo)

    # Escreve o cabeçalho
    escritor.writerow(cabecalho)

    # Escreve as 100.000 linhas
    for i in range(1, 100001):
        escritor.writerow(
            [
                i,
                f"Usuario_{i}",
                random.randint(18, 70),
                round(random.uniform(10.0, 5000.0), 2),
            ]
        )

print(f"Arquivo '{nome_arquivo}' gerado com sucesso!")