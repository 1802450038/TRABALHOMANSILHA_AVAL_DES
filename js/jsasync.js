const cluster = require('cluster');
const os = require('os');
const express = require('express');
const fs = require('fs').promises;

// Se for o processo "Mestre" (Gerente), ele cria os trabalhadores
if (cluster.isPrimary) {
    const numCPUs = 32; // Pega o número de núcleos do PC
    console.log(`Master process running. Forking ${numCPUs} workers...`);

    for (let i = 0; i < numCPUs; i++) {
        cluster.fork(); // Cria um workergi
    }

    cluster.on('exit', (worker) => {
        console.log(`Worker ${worker.process.pid} died`);
        cluster.fork(); // Substitui se morrer
    });

} else {
    // Se for um processo "Worker", ele roda o servidor Express
    const app = express();

    app.get('/', async (req, res) => {
        // Lógica igual ao anterior
        try {
            const data = await fs.readFile('posts.json', 'utf8');
            const items = JSON.parse(data).map(p => ({
                id: p.id,
                title: p.title.toUpperCase()
            }));
            res.json(items);
        } catch (err) {
            res.status(500).send(err.message);
        }
    });

    app.listen(8082, () => {
        // console.log('Worker listening...');
    });
}