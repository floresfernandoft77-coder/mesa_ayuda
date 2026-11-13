require("dotenv").config();          // lee .env SOLO en local; en la nube usa el panel
const path = require("path");
const express = require("express");
const mysql = require("mysql2/promise");

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

const pool = mysql.createPool({
  host: process.env.DB_HOST || "localhost",
  port: Number(process.env.DB_PORT || 3306),
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  connectionLimit: 5,
  // Muchos MySQL en la nube exigen TLS: poner DB_SSL=true en el panel
  ssl: process.env.DB_SSL === "true" ? { rejectUnauthorized: true } : undefined,
});

app.get("/api/health", async (req, res) => {
  try {
    await pool.query("SELECT 1");
    res.json({ ok: true, database: "conectada" });
  } catch (e) {
    console.error("Health:", e.code || e.message);   // sin contraseñas
    res.status(500).json({ ok: false, database: "sin conexion" });
  }
});

app.get("/api/tickets", async (req, res) => {
  try {
    const [rows] = await pool.query(
      "SELECT id, titulo, descripcion, solicitante, estado, creado FROM tickets ORDER BY id DESC LIMIT 100");
    res.json(rows);
  } catch (e) {
    console.error("GET tickets:", e.code || e.message);
    res.status(500).json({ error: "No se pudo consultar" });
  }
});

app.post("/api/tickets", async (req, res) => {
  const { titulo, descripcion, solicitante } = req.body || {};
  if (!titulo || !descripcion || !solicitante) {
    return res.status(400).json({ error: "Faltan campos" });
  }
  try {
    const [r] = await pool.query(
      "INSERT INTO tickets (titulo, descripcion, solicitante) VALUES (?, ?, ?)",
      [String(titulo).slice(0, 120), String(descripcion), String(solicitante).slice(0, 80)]);
    res.status(201).json({ id: r.insertId });
  } catch (e) {
    console.error("POST tickets:", e.code || e.message);
    res.status(500).json({ error: "No se pudo registrar" });
  }
});

const puerto = Number(process.env.PORT || 3000);
app.listen(puerto, "0.0.0.0", () => {
  console.log(`Aplicación iniciada en el puerto ${puerto}`);
});
