import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import sys

# Script para a FASE 2: Análise dos resultados coletados.
[cite_start]# [cite: 2]

INPUT_FILE = "resultados_workload.csv"

# Carrega os dados de RESULTADO do seu experimento
try:
    data = pd.read_csv(INPUT_FILE)
    if data.empty:
        print(f"Arquivo '{INPUT_FILE}' está vazio.")
        sys.exit(1)
except FileNotFoundError:
    print(f"Arquivo '{INPUT_FILE}' não encontrado.")
    print("Execute os scripts da pasta /scripts_etl primeiro para gerar este arquivo.")
    sys.exit(1)

print(f"Arquivo '{INPUT_FILE}' carregado com {len(data)} resultados.\n")

# --- 1. Técnica: Averaging (Média) ---
print("--- 1. Análise de Média ---")
grouped_data = data.groupby(['linguagem', 'modo', 'carga_registros']).mean(numeric_only=True)
print("Média de tempo de execução, memória e CPU:")
print(grouped_data[['tempo_total_s', 'pico_memoria_mb', 'media_cpu_percent']])
print("\n" + "="*50 + "\n")


# --- 2. Técnica: Clustering (K-Means) ---
print("--- 2. Análise de Clustering (K-Means) ---")
metrics = data[['tempo_total_s', 'pico_memoria_mb', 'media_cpu_percent']]
scaler = StandardScaler()
scaled_metrics = scaler.fit_transform(metrics)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
data['cluster'] = kmeans.fit_predict(scaled_metrics)
print("Centroides dos Clusters (Perfis de Workload):")
centroids = scaler.inverse_transform(kmeans.cluster_centers_)
print(pd.DataFrame(centroids, columns=['tempo_total_s', 'pico_memoria_mb', 'media_cpu_percent']))
print("\n" + "="*50 + "\n")


# --- 3. Técnica: Principal Component Analysis (PCA) ---
print("--- 3. Análise de Componentes Principais (PCA) ---")
pca = PCA(n_components=2)
pca.fit(scaled_metrics)
explained_variance = pca.explained_variance_ratio_

print(f"Componente Principal 1 explica: {explained_variance[0] * 100:.2f}% da variação")
print(f"Componente Principal 2 explica: {explained_variance[1] * 100:.2f}% da variação")
print(f"Total explicado (2 componentes): {sum(explained_variance) * 100:.2f}%")

print("\nImportância de cada métrica para o Componente Principal 1:")
loadings = pd.DataFrame(pca.components_.T, columns=['PC1', 'PC2'], index=['tempo_total_s', 'pico_memoria_mb', 'media_cpu_percent'])
print(loadings['PC1'])