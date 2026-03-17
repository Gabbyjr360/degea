// Minimal Express backend for product management
import express from 'express';
import sqlite3 from 'sqlite3';
import cors from 'cors';
const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// SQLite setup
const db = new sqlite3.Database('./products.db');
db.serialize(() => {
  db.run('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price TEXT, image TEXT, desc TEXT)');
});

// Get all products
app.get('/products', (req, res) => {
  db.all('SELECT * FROM products', [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

// Add product
app.post('/products', (req, res) => {
  const { name, price, image, desc } = req.body;
  db.run('INSERT INTO products (name, price, image, desc) VALUES (?, ?, ?, ?)', [name, price, image, desc], function(err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ id: this.lastID, name, price, image, desc });
  });
});

app.listen(PORT, () => {
  console.log(`Backend running on port ${PORT}`);
});
