CREATE DATABASE IF NOT EXISTS biblioteca;
USE biblioteca;

CREATE TABLE libros (
    isbn VARCHAR(20) PRIMARY KEY,
    titulo VARCHAR(100),
    autor VARCHAR(100),
    ejemplares_total INT,
    ejemplares_disponibles INT
);

CREATE TABLE prestamos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(20),
    usuario VARCHAR(100),
    fecha_prestamo DATE,
    fecha_devolucion DATE,
    renovaciones INT DEFAULT 0,
    estado ENUM('activo','devuelto') DEFAULT 'activo'
);

INSERT INTO libros VALUES
('123', 'Python para Todos', 'Downey', 5, 3),
('456', 'Sistemas Distribuidos', 'Tanenbaum', 3, 2),
('789', 'IA Moderna', 'Russell', 2, 1);