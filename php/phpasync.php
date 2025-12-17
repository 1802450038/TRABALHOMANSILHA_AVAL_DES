<?php
use OpenSwoole\Http\Server;
use OpenSwoole\Http\Request;
use OpenSwoole\Http\Response;

// Cria o servidor
$server = new Server("127.0.0.1", 8081);

// --- ADICIONE ESTE BLOCO ---
$server->set([
    'worker_num' => 4, // Define 4 processos (ajuste conforme seus núcleos de CPU)
    'reactor_num' => 4 // Threads para gerenciar conexões TCP
]);
// ---------------------------

$server->on("Start", function(Server $server) {
    echo "Swoole server running with 4 workers at http://127.0.0.1:8081\n";
});

// ... resto do código igual (on Request, etc) ...