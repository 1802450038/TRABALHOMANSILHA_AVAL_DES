import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import numpy as np

# Carrega os dados de RESULTADO do seu experimento
try:
    data = pd.read_csv("resultados_workload.csv")
except FileNotFoundError:
    print("Arquivo 'resultados_workload.csv' não encontrado.")
    print("Execute os scripts de ETL primeiro e salve os resultados neste arquivo.")
    exit()

print("Arquivo de resultados carregado com sucesso.\n")

# --- 1. Técnica: Averaging (Média) ---
print("--- 1. Análise de Média ---")
# Agrupa os resultados por linguagem, modo e carga
grouped_data = data.groupby(['linguagem', 'modo', 'carga_registros']).mean(numeric_only=True)
print("Média de tempo de execução, memória e CPU:")
print(grouped_data[['tempo_total_s', 'pico_memoria_mb', 'media_cpu_percent']])
print("\n" + "="*50 + "\n")


# --- 2. Preparação para Modelos (Clustering e PCA) ---
# Vamos focar apenas nas métricas de resultado para a análise
metrics = data[['tempo_total_s', 'pico_memoria_mb', 'media_cpu_percent']]
# É crucial escalar os dados, pois as métricas têm escalas diferentes
scaler = StandardScaler()
scaled_metrics = scaler.fit_transform(metrics)


# --- 3. Técnica: Clustering (K-Means) ---
print("--- 2. Análise de Clustering (K-Means) ---")
# Tenta agrupar os workloads em 3 tipos (ex: "rápidos", "médios", "lentos")
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
data['cluster'] = kmeans.fit_predict(scaled_metrics)

print("Centroides dos Clusters (Perfis de Workload):")
# Inverte a escala para que os centroides sejam legíveis nas unidades originais
centroids = scaler.inverse_transform(kmeans.cluster_centers_)
print(pd.DataFrame(centroids, columns=['tempo_total_s', 'pico_memoria_mb', 'media_cpu_percent']))
print("\nVeja quais execuções caíram em quais clusters:")
print(data[['linguagem', 'modo', 'carga_registros', 'cluster']])
print("\n" + "="*50 + "\n")


# --- 4. Técnica: Principal Component Analysis (PCA) ---
print("--- 3. Análise de Componentes Principais (PCA) ---")
# Reduz as 3 métricas (tempo, memória, cpu) para 2 componentes
pca = PCA(n_components=2)
principal_components = pca.fit_transform(scaled_metrics)

# Verifique quanta variação cada componente principal explica
explained_variance = pca.explained_variance_ratio_
print(f"Componente Principal 1 explica: {explained_variance[0] * 100:.2f}% da variação")
print(f"Componente Principal 2 explica: {explained_variance[1] * 100:.2f}% da variação")
print(f"Total explicado (2 componentes): {sum(explained_variance) * 100:.2f}%")
print("\nImportância de cada métrica para o Componente Principal 1:")
loadings = pd.DataFrame(pca.components_.T, columns=['PC1', 'PC2'], index=['tempo_total_s', 'pico_memoria_mb', 'media_cpu_percent'])
print(loadings['PC1'])
print("\n(Um valor alto aqui indica que a métrica é o principal fator de diferenciação)")