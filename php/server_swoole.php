<?php
use OpenSwoole\Http\Server;
use OpenSwoole\Http\Request;
use OpenSwoole\Http\Response;

// Cria o servidor na porta 8081
$server = new Server("127.0.0.1", 8081);

$server->on("Start", function(Server $server) {
    echo "Swoole http server is started at http://127.0.0.1:8081\n";
});

$server->on("Request", function(Request $request, Response $response) {
    // Configura o header
    $response->header("Content-Type", "application/json");

    // Lê o arquivo (O OpenSwoole gerencia a concorrência do processo, 
    // mesmo usando funções que seriam bloqueantes no PHP padrão)
    $data = json_decode(file_get_contents(__DIR__ . '/posts.json'));

    // Processamento dos dados
    $items = array_map(function ($item) {
        return [
            'id' => $item->id,
            'title' => ucwords($item->title)
        ];
    }, $data);

    // Envia a resposta
    $response->end(json_encode($items));
});

$server->start();
