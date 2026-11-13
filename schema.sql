-- Estructura de la Mesa de Ayuda (ejecutar en la base MySQL del entorno PUBLICADO)
-- Solo datos FICTICIOS.
CREATE TABLE IF NOT EXISTS tickets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(120) NOT NULL,
  descripcion TEXT NOT NULL,
  solicitante VARCHAR(80) NOT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'abierto',
  creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO tickets (titulo, descripcion, solicitante) VALUES
('Proyector no enciende', 'Ticket de prueba (dato ficticio).', 'Usuario Demo 1'),
('Sin internet en aula 3', 'Ticket de prueba (dato ficticio).', 'Usuario Demo 2');
