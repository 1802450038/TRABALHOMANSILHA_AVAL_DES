import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Script para análise básica (Média) dos resultados.
public class AnaliseWorkload {

    // Classe interna para guardar as métricas de um grupo
    static class Stats {
        List<Double> tempos = new ArrayList<>();
        List<Double> memorias = new ArrayList<>();
        List<Double> cpus = new ArrayList<>();

        public void add(double tempo, double memoria, double cpu) {
            tempos.add(tempo);
            memorias.add(memoria);
            cpus.add(cpu);
        }

        public String getAverages() {
            double avgTempo = tempos.stream().mapToDouble(d -> d).average().orElse(0.0);
            double avgMemoria = memorias.stream().mapToDouble(d -> d).average().orElse(0.0);
            double avgCpu = cpus.stream().mapToDouble(d -> d).average().orElse(0.0);
            return String.format("%-15.2f | %-15.2f | %.2f", avgTempo, avgMemoria, avgCpu);
        }
    }

    public static void main(String[] args) {
        System.out.println("--- 1. Análise de Média (Java) ---");

        String csvFile = "resultados_workload.csv"; // Deve estar na raiz
        Map<String, Stats> groupedStats = new HashMap<>();
        
        try (BufferedReader br = new BufferedReader(new FileReader(csvFile))) {
            String line;
            // Pular cabeçalho
            String[] headers = br.readLine().split(","); 
            int langIdx = findIndex(headers, "linguagem");
            int modoIdx = findIndex(headers, "modo");
            int cargaIdx = findIndex(headers, "carga_registros");
            int tempoIdx = findIndex(headers, "tempo_total_s");
            int memIdx = findIndex(headers, "pico_memoria_mb");
            int cpuIdx = findIndex(headers, "media_cpu_percent");


            while ((line = br.readLine()) != null) {
                String[] values = line.split(",");
                
                String key = values[langIdx] + "_" + values[modoIdx] + "_" + values[cargaIdx];
                double tempo = Double.parseDouble(values[tempoIdx]);
                double memoria = Double.parseDouble(values[memIdx]);
                double cpu = Double.parseDouble(values[cpuIdx]);

                groupedStats.putIfAbsent(key, new Stats());
                groupedStats.get(key).add(tempo, memoria, cpu);
            }

            // Imprimir resultados
            System.out.printf("%-40s | %-15s | %-15s | %s\n", "Grupo", "Média Tempo", "Média Memória", "Média CPU");
            System.out.println(String.join("", java.util.Collections.nCopies(85, "-")));

            for (Map.Entry<String, Stats> entry : groupedStats.entrySet()) {
                System.out.printf("%-40s | %s\n", entry.getKey(), entry.getValue().getAverages());
            }

        } catch (IOException e) {
            System.err.println("Erro: Arquivo 'resultados_workload.csv' não encontrado na raiz.");
        } catch (Exception e) {
            System.err.println("Erro ao processar o arquivo: " + e.getMessage());
        }
    }

    private static int findIndex(String[] headers, String colName) {
        for (int i = 0; i < headers.length; i++) {
            if (headers[i].equals(colName)) {
                return i;
            }
        }
        return -1;
    }
}