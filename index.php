<?php
// Script para análise básica (Média) dos resultados.
echo "--- 1. Análise de Média (PHP) ---\n";

$file_path = __DIR__ . '/../resultados_workload.csv';
$grouped_stats = [];

if (!file_exists($file_path) || !($handle = fopen($file_path, "r"))) {
    die("Erro: Arquivo 'resultados_workload.csv' não encontrado na raiz.\n");
}

// Ler o cabeçalho
$headers = fgetcsv($handle);
$key_indices = [
    'lang' => array_search('linguagem', $headers),
    'modo' => array_search('modo', $headers),
    'carga' => array_search('carga_registros', $headers),
];
$metric_indices = [
    'tempo' => array_search('tempo_total_s', $headers),
    'mem' => array_search('pico_memoria_mb', $headers),
    'cpu' => array_search('media_cpu_percent', $headers),
];

// Ler os dados
while (($row = fgetcsv($handle)) !== FALSE) {
    $key = sprintf(
        "%s_%s_%s",
        $row[$key_indices['lang']],
        $row[$key_indices['modo']],
        $row[$key_indices['carga']]
    );
    if (!isset($grouped_stats[$key])) {
        $grouped_stats[$key] = ['tempo' => [], 'mem' => [], 'cpu' => []];
    }
    $grouped_stats[$key]['tempo'][] = (float) $row[$metric_indices['tempo']];
    $grouped_stats[$key]['mem'][] = (float) $row[$metric_indices['mem']];
    $grouped_stats[$key]['cpu'][] = (float) $row[$metric_indices['cpu']];
}
fclose($handle);

// Calcular e exibir a média
echo str_pad("Grupo", 40) . str_pad("Média Tempo", 15) . str_pad("Média Memória", 15) . "Média CPU\n";
echo str_repeat("-", 85) . "\n";

foreach ($grouped_stats as $key => $metrics) {
    $avg_tempo = count($metrics['tempo']) ? array_sum($metrics['tempo']) / count($metrics['tempo']) : 0;
    $avg_mem = count($metrics['mem']) ? array_sum($metrics['mem']) / count($metrics['mem']) : 0;
    $avg_cpu = count($metrics['cpu']) ? array_sum($metrics['cpu']) / count($metrics['cpu']) : 0;

    echo str_pad($key, 40);
    echo str_pad(number_format($avg_tempo, 2), 15);
    echo str_pad(number_format($avg_mem, 2), 15);
    echo number_format($avg_cpu, 2) . "\n";
}
?>