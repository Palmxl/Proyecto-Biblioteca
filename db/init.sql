CREATE DATABASE IF NOT EXISTS biblioteca;
USE biblioteca;

CREATE TABLE IF NOT EXISTS libros (
  isbn VARCHAR(20) PRIMARY KEY,
  titulo VARCHAR(100),
  autor VARCHAR(100),
  ejemplares_total INT,
  ejemplares_disponibles INT
);

CREATE TABLE IF NOT EXISTS prestamos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  isbn VARCHAR(20),
  usuario VARCHAR(100),
  fecha_prestamo DATE,
  fecha_devolucion DATE,
  renovaciones INT DEFAULT 0,
  estado ENUM('activo','devuelto') DEFAULT 'activo',
  INDEX (isbn, usuario, estado)
);

