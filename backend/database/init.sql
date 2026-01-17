-- =========================================
-- BASE DE DATOS
-- =========================================
CREATE DATABASE IF NOT EXISTS goalAppBD
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE goalAppBD;

-- =========================================
-- USUARIOS Y ROLES
-- =========================================
CREATE TABLE usuarios (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  contraseña_hash VARCHAR(255) NOT NULL,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
  id_rol INT AUTO_INCREMENT PRIMARY KEY,
  nombre_rol VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE usuarios_roles (
  id_usuario INT NOT NULL,
  id_rol INT NOT NULL,
  PRIMARY KEY (id_usuario, id_rol),
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
    ON DELETE CASCADE ON UPDATE CASCADE
);

-- =========================================
-- LIGAS, EQUIPOS Y JUGADORES
-- =========================================
CREATE TABLE ligas (
  id_liga INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  temporada VARCHAR(20),
  creado_por INT NOT NULL,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (creado_por) REFERENCES usuarios(id_usuario)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE equipos (
  id_equipo INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  escudo VARCHAR(255),
  colores VARCHAR(100),
  id_liga INT NOT NULL,
  id_entrenador INT,
  id_delegado INT,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_liga) REFERENCES ligas(id_liga)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_entrenador) REFERENCES usuarios(id_usuario)
    ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (id_delegado) REFERENCES usuarios(id_usuario)
    ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE jugadores (
  id_jugador INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT NOT NULL UNIQUE,
  id_equipo INT NOT NULL,
  posicion VARCHAR(30),
  dorsal INT,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_jugadores_equipo ON jugadores(id_equipo);

-- =========================================
-- PARTIDOS Y COMPETICIÓN
-- =========================================
CREATE TABLE partidos (
  id_partido INT AUTO_INCREMENT PRIMARY KEY,
  id_liga INT NOT NULL,
  id_equipo_local INT NOT NULL,
  id_equipo_visitante INT NOT NULL,
  fecha_partido DATETIME NOT NULL,
  goles_local INT DEFAULT 0,
  goles_visitante INT DEFAULT 0,
  estado ENUM('programado','en_juego','finalizado') DEFAULT 'programado',
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_liga) REFERENCES ligas(id_liga)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_equipo_local) REFERENCES equipos(id_equipo)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (id_equipo_visitante) REFERENCES equipos(id_equipo)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_partidos_liga ON partidos(id_liga);
CREATE INDEX idx_partidos_fecha ON partidos(fecha_partido);

CREATE TABLE delegados_partido (
  id_delegado_partido INT AUTO_INCREMENT PRIMARY KEY,
  id_partido INT NOT NULL,
  id_usuario INT NOT NULL,
  FOREIGN KEY (id_partido) REFERENCES partidos(id_partido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    ON DELETE CASCADE ON UPDATE CASCADE
);

-- =========================================
-- EVENTOS Y ESTADÍSTICAS
-- =========================================
CREATE TABLE eventos_partido (
  id_evento INT AUTO_INCREMENT PRIMARY KEY,
  id_partido INT NOT NULL,
  id_jugador INT,
  tipo_evento ENUM(
    'gol','tarjeta_amarilla','tarjeta_roja',
    'cambio','incidencia','MVP'
  ) NOT NULL,
  minuto INT,
  creado_por INT NOT NULL,
  FOREIGN KEY (id_partido) REFERENCES partidos(id_partido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (creado_por) REFERENCES usuarios(id_usuario)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_eventos_partido ON eventos_partido(id_partido);
CREATE INDEX idx_eventos_jugador ON eventos_partido(id_jugador);

CREATE TABLE clasificacion (
  id_clasificacion INT AUTO_INCREMENT PRIMARY KEY,
  id_liga INT NOT NULL,
  id_equipo INT NOT NULL,
  partidos_jugados INT DEFAULT 0,
  victorias INT DEFAULT 0,
  empates INT DEFAULT 0,
  derrotas INT DEFAULT 0,
  goles_favor INT DEFAULT 0,
  goles_contra INT DEFAULT 0,
  puntos INT DEFAULT 0,
  UNIQUE (id_liga, id_equipo),
  FOREIGN KEY (id_liga) REFERENCES ligas(id_liga)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_clasificacion_liga ON clasificacion(id_liga);

CREATE TABLE estadisticas_jugador (
  id_estadistica INT AUTO_INCREMENT PRIMARY KEY,
  id_jugador INT NOT NULL UNIQUE,
  goles INT DEFAULT 0,
  tarjetas_amarillas INT DEFAULT 0,
  tarjetas_rojas INT DEFAULT 0,
  FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

-- =========================================
-- FORMACIONES Y ALINEACIONES
-- =========================================
CREATE TABLE formaciones (
  id_formacion INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(20) NOT NULL,
  descripcion TEXT,
  creado_por INT NOT NULL,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (creado_por) REFERENCES usuarios(id_usuario)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE posiciones_formacion (
  id_posicion_formacion INT AUTO_INCREMENT PRIMARY KEY,
  id_formacion INT NOT NULL,
  codigo_posicion VARCHAR(10) NOT NULL,
  nombre_posicion VARCHAR(50),
  posicion_x DECIMAL(5,2),
  posicion_y DECIMAL(5,2),
  FOREIGN KEY (id_formacion) REFERENCES formaciones(id_formacion)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE formaciones_equipo (
  id_formacion_equipo INT AUTO_INCREMENT PRIMARY KEY,
  id_equipo INT NOT NULL,
  id_formacion INT NOT NULL,
  es_por_defecto BOOLEAN DEFAULT FALSE,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_formacion) REFERENCES formaciones(id_formacion)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE formaciones_partido (
  id_formacion_partido INT AUTO_INCREMENT PRIMARY KEY,
  id_partido INT NOT NULL,
  id_equipo INT NOT NULL,
  id_formacion INT NOT NULL,
  FOREIGN KEY (id_partido) REFERENCES partidos(id_partido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_formacion) REFERENCES formaciones(id_formacion)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE alineaciones_partido (
  id_alineacion INT AUTO_INCREMENT PRIMARY KEY,
  id_partido INT NOT NULL,
  id_equipo INT NOT NULL,
  id_jugador INT NOT NULL,
  id_posicion_formacion INT NOT NULL,
  es_titular BOOLEAN DEFAULT TRUE,
  FOREIGN KEY (id_partido) REFERENCES partidos(id_partido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (id_posicion_formacion) REFERENCES posiciones_formacion(id_posicion_formacion)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_alineaciones_partido ON alineaciones_partido(id_partido);

-- =========================================
-- VISTAS
-- =========================================
CREATE VIEW vw_clasificacion_liga AS
SELECT c.id_liga, e.nombre AS equipo,
       c.partidos_jugados, c.victorias, c.empates, c.derrotas,
       c.goles_favor, c.goles_contra, c.puntos
FROM clasificacion c
JOIN equipos e ON c.id_equipo = e.id_equipo;

CREATE VIEW vw_partidos_detalle AS
SELECT p.id_partido, p.fecha_partido, p.estado,
       el.nombre AS equipo_local,
       ev.nombre AS equipo_visitante,
       p.goles_local, p.goles_visitante
FROM partidos p
JOIN equipos el ON p.id_equipo_local = el.id_equipo
JOIN equipos ev ON p.id_equipo_visitante = ev.id_equipo;

CREATE VIEW vw_jugadores_equipo AS
SELECT j.id_jugador, u.nombre AS jugador,
       e.nombre AS equipo, j.posicion, j.dorsal
FROM jugadores j
JOIN usuarios u ON j.id_usuario = u.id_usuario
JOIN equipos e ON j.id_equipo = e.id_equipo;
