<?php
// Requer `pdo_mysql` e a extensão `swoole`

// --- Configurações ---
$db_config_sync = [
    'dsn' => 'mysql:host=localhost;dbname=trabalho_pep;charset=utf8mb4',
    'user' => 'root',
    'pass' => 'seu_password_aqui'
];
$db_config_async = [
    'host' => 'localhost', 'user' => 'root', 'password' => 'seu_password_aqui', 'database' => 'trabalho_pep',
];
$pep_file_path = __DIR__ . '/../dados_entrada/202210_PEP.csv';
$result_file_path = __DIR__ . '/../resultados_workload.csv';
// ---------------------

// Colunas que vamos ler
const COL_CPF = 0;
const COL_NOME = 1;
const COL_CARGO_DESC = 3;
const COL_CIDADE_NOME = 5;

function save_result($language, $mode, $architecture, $load_size, $time_s, $peak_mem_mb, $cpu_percent) {
    global $result_file_path;
    $file_exists = file_exists($result_file_path);
    
    $handle = fopen($result_file_path, 'a');
    if (!$file_exists) {
        fputcsv($handle, ["linguagem", "modo", "arquitetura", "carga_registros", "tempo_total_s", "pico_memoria_mb", "media_cpu_percent"]);
    }
    fputcsv($handle, [$language, $mode, $architecture, $load_size, number_format($time_s, 2), number_format($peak_mem_mb, 2), number_format($cpu_percent, 2)]);
    fclose($handle);
    echo "Resultado salvo em $result_file_path\n";
}

// --- MODO SÍNCRONO (PDO) ---
function run_sync_etl($limit) {
    global $db_config_sync, $pep_file_path;
    
    $pdo = new PDO($db_config_sync['dsn'], $db_config_sync['user'], $db_config_sync['pass']);
    $stmt_cidade = $pdo->prepare("SELECT id FROM cidades WHERE org_nome = ?");
    $stmt_cargo = $pdo->prepare("SELECT id FROM cargos WHERE func_desc = ?");
    $stmt_insert = $pdo->prepare("INSERT INTO pessoas (cpf, nome_pep, cidade_id, cargo_id) VALUES (?, ?, ?, ?)");

    $handle = fopen($pep_file_path, "r");
    fgetcsv($handle); // Pular cabeçalho
    $count = 0;

    $pdo->beginTransaction();
    while (($row = fgetcsv($handle)) !== FALSE && $count < $limit) {
        // 1. Buscar Cidade
        $stmt_cidade->execute([$row[COL_CIDADE_NOME]]);
        $cidade_id = $stmt_cidade->fetchColumn() ?: null;
        
        // 2. Buscar Cargo
        $stmt_cargo->execute([$row[COL_CARGO_DESC]]);
        $cargo_id = $stmt_cargo->fetchColumn() ?: null;
        
        // 3. Inserir
        $stmt_insert->execute([$row[COL_CPF], $row[COL_NOME], $cidade_id, $cargo_id]);
        $count++;
    }
    $pdo->commit();
    fclose($handle);
}

// --- MODO ASSÍNCRONO (Swoole) ---
use Swoole\Coroutine;
use Swoole\Database\MySQL\Coroutine as MySQLCoroutine;
use Swoole\Coroutine\WaitGroup;

async function process_row_async(MySQLCoroutine $db, array $row_data) {
    [$cpf, $nome, $cargo_desc, $cidade_nome] = $row_data;
    
    // 1. Buscar Cidade
    $stmt_cidade = $db->prepare("SELECT id FROM cidades WHERE org_nome = ?");
    $cidade_id = ($stmt_cidade->execute([$cidade_nome]))[0]['id'] ?? null;
    
    // 2. Buscar Cargo
    $stmt_cargo = $db->prepare("SELECT id FROM cargos WHERE func_desc = ?");
    $cargo_id = ($stmt_cargo->execute([$cargo_desc]))[0]['id'] ?? null;
    
    // 3. Inserir
    $stmt_insert = $db->prepare("INSERT INTO pessoas (cpf, nome_pep, cidade_id, cargo_id) VALUES (?, ?, ?, ?)");
    $stmt_insert->execute([$cpf, $nome, $cidade_id, $cargo_id]);
}

function run_async_etl($limit) {
    global $db_config_async, $pep_file_path;
    
    $pool = new Swoole\Coroutine\MySQL\Pool($db_config_async, 64);
    $handle = fopen($pep_file_path, "r");
    fgetcsv($handle); // Pular cabeçalho
    $count = 0;
    $wg = new WaitGroup();

    while (($row = fgetcsv($handle)) !== FALSE && $count < $limit) {
        $data = [$row[COL_CPF], $row[COL_NOME], $row[COL_CARGO_DESC], $row[COL_CIDADE_NOME]];
        $wg->add();
        Coroutine::create(function () use ($pool, $data, $wg) {
            $db = $pool->get();
            await process_row_async($db, $data);
            $pool->put($db);
            $wg->done();
        });
        $count++;
    }
    
    $wg->wait();
    fclose($handle);
    $pool->close();
}

// --- Execução Principal ---
if ($argc < 5) {
    echo "Uso: php etl_php.php [sync|async] [limite_registros] [arquitetura] [cpu_medida]\n";
    echo "Ex: php etl_php.php async 10000 intel 45.5\n";
    exit(1);
}

$MODE = $argv[1];
$LIMIT = (int)$argv[2];
$ARCH = $argv[3];
$CPU_PERCENT = (float)$argv[4]; // Medição de CPU é complexa, melhor passar como argumento

// 1. Executar e Medir
$start_time = microtime(true);

if ($MODE == 'sync') {
    echo "\n--- Iniciando ETL Síncrono (PHP) para $LIMIT registros ---\n";
    run_sync_etl($LIMIT);
} elseif ($MODE == 'async') {
    echo "\n--- Iniciando ETL Assíncrono (PHP/Swoole) para $LIMIT registros ---\n";
    Swoole\Coroutine\run(function () use ($LIMIT) {
        run_async_etl($LIMIT);
    });
} else {
    echo "Modo '$MODE' desconhecido. Use 'sync' ou 'async'.\n";
    exit(1);
}

$end_time = microtime(true);
$total_time_s = $end_time - $start_time;

// Medir Pico de Memória (em MB)
$peak_mem_bytes = memory_get_peak_usage(true);
$peak_mem_mb = $peak_mem_bytes / 1024.0 / 1024.0;

echo "--- Concluído em " . number_format($total_time_s, 2) . " segundos ---\n";
echo "--- Pico de Memória: " . number_format($peak_mem_mb, 2) . " MB ---\n";

// 3. Salvar resultados
save_result("php", $MODE, $ARCH, $LIMIT, $total_time_s, $peak_mem_mb, $CPU_PERCENT);
?>