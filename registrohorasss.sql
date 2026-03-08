-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 08-03-2026 a las 20:28:58
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `registrohorasss`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alumnos`
--

CREATE TABLE `alumnos` (
  `id_alumno` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `nombre_completo` varchar(150) NOT NULL,
  `num_servicio` varchar(50) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_termino` date NOT NULL,
  `activo` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bitacora_horas`
--

CREATE TABLE `bitacora_horas` (
  `id_registro` int(11) NOT NULL,
  `id_alumno` int(11) NOT NULL,
  `fecha_actividad` date NOT NULL,
  `horas` decimal(4,2) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `fecha_captura` timestamp NOT NULL DEFAULT current_timestamp(),
  `tipo_dia` enum('habil','inhabil','vacaciones') DEFAULT 'habil'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `rol` enum('admin','alumno') NOT NULL DEFAULT 'alumno',
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vista_progreso_alumnos`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `vista_progreso_alumnos` (
`id_alumno` int(11)
,`nombre_completo` varchar(150)
,`num_servicio` varchar(50)
,`fecha_inicio` date
,`fecha_termino` date
,`horas_totales_acumuladas` decimal(26,2)
,`dias_asistidos` bigint(21)
);

-- --------------------------------------------------------

--
-- Estructura para la vista `vista_progreso_alumnos`
--
DROP TABLE IF EXISTS `vista_progreso_alumnos`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vista_progreso_alumnos`  AS SELECT `a`.`id_alumno` AS `id_alumno`, `a`.`nombre_completo` AS `nombre_completo`, `a`.`num_servicio` AS `num_servicio`, `a`.`fecha_inicio` AS `fecha_inicio`, `a`.`fecha_termino` AS `fecha_termino`, coalesce(sum(`b`.`horas`),0) AS `horas_totales_acumuladas`, count(case when `b`.`horas` > 0 then 1 end) AS `dias_asistidos` FROM (`alumnos` `a` left join `bitacora_horas` `b` on(`a`.`id_alumno` = `b`.`id_alumno`)) GROUP BY `a`.`id_alumno`, `a`.`nombre_completo`, `a`.`num_servicio`, `a`.`fecha_inicio`, `a`.`fecha_termino` ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `alumnos`
--
ALTER TABLE `alumnos`
  ADD PRIMARY KEY (`id_alumno`),
  ADD UNIQUE KEY `id_usuario` (`id_usuario`),
  ADD UNIQUE KEY `num_servicio` (`num_servicio`);

--
-- Indices de la tabla `bitacora_horas`
--
ALTER TABLE `bitacora_horas`
  ADD PRIMARY KEY (`id_registro`),
  ADD UNIQUE KEY `idx_alumno_fecha` (`id_alumno`,`fecha_actividad`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `alumnos`
--
ALTER TABLE `alumnos`
  MODIFY `id_alumno` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `bitacora_horas`
--
ALTER TABLE `bitacora_horas`
  MODIFY `id_registro` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=138;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `alumnos`
--
ALTER TABLE `alumnos`
  ADD CONSTRAINT `fk_usuario_alumno` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE;

--
-- Filtros para la tabla `bitacora_horas`
--
ALTER TABLE `bitacora_horas`
  ADD CONSTRAINT `fk_alumno_bitacora` FOREIGN KEY (`id_alumno`) REFERENCES `alumnos` (`id_alumno`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
