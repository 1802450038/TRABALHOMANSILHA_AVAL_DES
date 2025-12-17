<?php
// phpsync.php
// Este arquivo deve ser rodado com o servidor embutido do PHP (Single Thread/Blocking por padrão)
// Comando: php -S 127.0.0.1:8081 phpsync.php

header('Content-Type: application/json');

try {
    // 1. Leitura Síncrona/Bloqueante do arquivo
    // O script para aqui e espera o disco ler o arquivo inteiro
    $content = file_get_contents('posts.json');
    
    if ($content === false) {
        throw new Exception("Erro ao ler o arquivo");
    }

    $posts = json_decode($content, true);

    // 2. Processamento de dados
    $items = array_map(function($post) {
        return [
            'id' => $post['id'],
            'title' => strtoupper($post['title']) // Converte para maiúsculas
        ];
    }, $posts);

    // 3. Retorno da resposta
    echo json_encode($items);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
?>
<!-- Para rodar -->
<!-- php -S 127.0.0.1:8081 phpsync.php -->