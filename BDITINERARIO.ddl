CREATE TABLE Itinerario (
    lugar VARCHAR(255) NOT NULL,
    ciudad INT NOT NULL, // Foranea a Cities
    pais INT NOT NULL, // Foranea a Countries
    dia INT NOT NULL,
    costo DECIMAL(10,2) NOT NULL, //Costo del viaje
    estado VARCHAR(20) NOT NULL, //Estado del viaje
    Viaje INT NOT NULL, // Foranea a Viaje
    Clima INT NOT NULL, // Foranea a Clima
    Transporte INT NOT NULL // Foranea a Transporte
);

CREATE TABLE Viaje (
    presupuesto DECIMAL(10,2) NOT NULL,
    dia_salida DATE NOT NULL,
    ciudad_salida INT NOT NULL, // Foranea a Cities
    duracion_viaje INT NOT NULL, //Duración del viaje
    estado VARCHAR(20) NOT NULL //Estado del viaje
);

CREATE TABLE Clima (
    fecha DATE NOT NULL,
    temperatura_actual FLOAT NOT NULL,
    temperatura_sensacion FLOAT NOT NULL,
    descripcion VARCHAR(100) NOT NULL,
    estado_clima VARCHAR(50) NOT NULL,
    humedad INT NOT NULL,
    velocidad_viento FLOAT NOT NULL,
    direccion_viento INT NOT NULL,
    probabilidad_lluvia FLOAT NOT NULL
);

CREATE TABLE Actividad (
    turno VARCHAR(10) NOT NULL, //Turno de la actividad (mañana, tarde, noche)
    orden INT NOT NULL, //Orden de la actividad
    estado VARCHAR(20) NOT NULL, //Estado de la actividad
    Itinerario INT NOT NULL // Foranea a Itinerario
);

CREATE TABLE Transporte (
    Tipo_Transporte INT NOT NULL, // Foranea a Tipo_Transporte
    nombre VARCHAR(100) NOT NULL, //Nombre del transporte
    estado BOOLEAN NOT NULL DEFAULT TRUE //Estado del transporte
);

CREATE TABLE Tipo_Transporte (
    nombre VARCHAR(100) NOT NULL,
    estado BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE Lugar (
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT NOT NULL,
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    ubicacion VARCHAR(255) NOT NULL,
    Tipo_Lugar INT NOT NULL
);

CREATE TABLE Actividad_Lugar (
    Actividad INT NOT NULL,
    Lugar INT NOT NULL,
    PRIMARY KEY (Actividad, Lugar)
);

CREATE TABLE Tipo_Lugar (
    nombre VARCHAR(100) NOT NULL, //Nombre del tipo de lugar
    estado BOOLEAN NOT NULL DEFAULT TRUE //Estado del tipo de lugar
);

ALTER TABLE Itinerario ADD CONSTRAINT FKItinerario31050 FOREIGN KEY (Viaje) REFERENCES Viaje (id);
ALTER TABLE Itinerario ADD CONSTRAINT FKItinerario242089 FOREIGN KEY (Clima) REFERENCES Clima (id);
ALTER TABLE Actividad ADD CONSTRAINT FKActividad696410 FOREIGN KEY (Itinerario) REFERENCES Itinerario (id);
ALTER TABLE Itinerario ADD CONSTRAINT FKItinerario645840 FOREIGN KEY (Transporte) REFERENCES Transporte (id);
ALTER TABLE Transporte ADD CONSTRAINT FKTransporte561109 FOREIGN KEY (Tipo_Transporte) REFERENCES Tipo_Transporte (id);
ALTER TABLE Actividad_Lugar ADD CONSTRAINT FKActividad_135155 FOREIGN KEY (Actividad) REFERENCES Actividad (id);
ALTER TABLE Actividad_Lugar ADD CONSTRAINT FKActividad_761507 FOREIGN KEY (Lugar) REFERENCES Lugar (id);
ALTER TABLE Lugar ADD CONSTRAINT FKLugar325112 FOREIGN KEY (Tipo_Lugar) REFERENCES Tipo_Lugar (id);



/*


CITIES Countries STATES


*/
INSERT INTO `states` (`id`, `country_id`, `name`, `latitude`, `longitude`, `is_active`, `created_at`, `updated_at`, `deleted_at`) VALUES
(1, 70, 'Southern Nations, Nationalities, and Peoples\' Region', '6.51569110', '36.95410700', 1, '2024-08-18 19:21:44', '2024-08-18 19:21:44', NULL);

INSERT INTO `countries` (`id`, `name`, `iso2`, `iso3`, `numeric_code`, `phonecode`, `capital`, `currency`, `currency_name`, `currency_symbol`, `tld`, `native`, `region`, `subregion`, `timezones`, `translations`, `latitude`, `longitude`, `emoji`, `emojiU`, `flag`, `is_active`, `created_at`, `updated_at`, `deleted_at`) VALUES
(1, 'Afghanistan', 'AF', 'AFG', '004', '93', 'Kabul', 'AFN', 'Afghan afghani', '؋', '.af', 'افغانستان', 'Asia', 'Southern Asia', '[{\"zoneName\":\"Asia\\/Kabul\",\"gmtOffset\":16200,\"gmtOffsetName\":\"UTC+04:30\",\"abbreviation\":\"AFT\",\"tzName\":\"Afghanistan Time\"}]', '{\"ar\":\"\\u0627\\u0641\\u063a\\u0627\\u0646\\u0633\\u062a\\u0627\\u0646\",\"kr\":\"\\uc544\\ud504\\uac00\\ub2c8\\uc2a4\\ud0c4\",\"br\":\"Afeganist\\u00e3o\",\"pt\":\"Afeganist\\u00e3o\",\"nl\":\"Afghanistan\",\"hr\":\"Afganistan\",\"fa\":\"\\u0627\\u0641\\u063a\\u0627\\u0646\\u0633\\u062a\\u0627\\u0646\",\"de\":\"Afghanistan\",\"es\":\"Afganist\\u00e1n\",\"fr\":\"Afghanistan\",\"ja\":\"\\u30a2\\u30d5\\u30ac\\u30cb\\u30b9\\u30bf\\u30f3\",\"it\":\"Afghanistan\",\"cn\":\"\\u963f\\u5bcc\\u6c57\"}', '33.00000000', '65.00000000', '🇦🇫', 'U+1F1E6 U+1F1EB', 1, 1, '2024-08-18 19:21:29', '2024-08-18 19:21:29', NULL);

INSERT INTO `cities` (`id`, `country_id`, `state_id`, `name`, `latitude`, `longitude`, `is_active`, `created_at`, `updated_at`, `deleted_at`) VALUES
(1, 6, 488, 'Andorra la Vella', '42.50779000', '1.52109000', 1, '2024-08-18 19:22:13', '2024-08-18 19:22:13', NULL);
