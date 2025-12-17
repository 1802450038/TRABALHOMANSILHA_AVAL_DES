const express = require('express');
const fs = require('fs').promises; // Usando a versão Promessa do FileSystem
const app = express();

app.get('/', async (req, res) => {
    try {
        // Leitura assíncrona com await
        const data = await fs.readFile('posts.json', 'utf8');
        const posts = JSON.parse(data);

        const items = posts.map(post => ({
            id: post.id,
            title: post.title.toUpperCase()
        }));

        res.json(items);
    } catch (err) {
        res.status(500).send(err.message);
    }
});

app.listen(8082, () => {
    console.log('Node async server running on port 8082');
});