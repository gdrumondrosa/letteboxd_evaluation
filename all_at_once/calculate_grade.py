import pandas as pd
import numpy as np

# Função para calcular a nota final robusta
def calcular_nota_final(distribuicao):
    pesos = np.array([0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5])
    votos = np.array(distribuicao)
    total_votos = np.sum(votos)
    
    # Evitar divisão por zero
    if total_votos == 0:
        return 0.0

    # Cálculo da média ponderada simples
    media_ponderada = np.dot(pesos, votos) / total_votos

    # Cálculo da moda ponderada (nota com maior concentração relativa)
    moda_ponderada = pesos[np.argmax(votos / total_votos)]

    # Cálculo do desvio ponderado para penalizar ou favorecer extremos
    desvio_ponderado = np.std(votos * pesos / total_votos)

    # Ajuste para extremidade baseado em distribuição
    ajuste_extremo = media_ponderada + (moda_ponderada - media_ponderada) * desvio_ponderado

    # Arredondar para o valor mais próximo das opções possíveis
    nota_final = min(pesos, key=lambda x: abs(x - ajuste_extremo))
    return nota_final

# Dados de entrada (substitua pelo caminho do seu arquivo CSV)
csv_input = 'movie_grades.csv'
csv_output = 'final_movie_grades.csv'

# Ler o CSV
df = pd.read_csv(csv_input)

# Transformar a coluna de notas de string para lista
df['Notas'] = df['Notas'].apply(eval)

# Calcular a nota final para cada filme
df['Nota Final'] = df['Notas'].apply(calcular_nota_final)

# Salvar o resultado como um novo CSV
df[['Filme', 'Slug', 'Nota Final']].to_csv(csv_output, index=False)