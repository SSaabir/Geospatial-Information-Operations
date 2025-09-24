CREATE TABLE weather_data (
    id SERIAL PRIMARY KEY,
    country TEXT,
    statedistrict TEXT,
    datetime DATE,
    tempmax FLOAT,
    tempmin FLOAT,
    temp FLOAT,
    humidity FLOAT,
    rain BOOLEAN,
    rainsum FLOAT,
    snow BOOLEAN,
    snowdepth FLOAT,
    windgust FLOAT,
    windspeed FLOAT,
    winddir FLOAT,
    sealevelpressure FLOAT,
    cloudcover FLOAT,
    visibility FLOAT,
    solarradiation FLOAT,
    solarenergy FLOAT,
    uvindex FLOAT,
    sunrise TIME,
    sunset TIME,
    moonphase FLOAT,
    conditions TEXT,
    description TEXT,
    icon TEXT
);


CREATE TABLE weather_stations (
    id SERIAL PRIMARY KEY,
    name TEXT,
    latitude FLOAT,
    longitude FLOAT,
    elevation FLOAT
);


CREATE TABLE air_quality_data (
    id SERIAL PRIMARY KEY,
    country TEXT,
    statedistrict TEXT,
    datetime DATE,              -- date of the measurement
    pm10 FLOAT,                 -- particulate matter ≤10µm
    pm2_5 FLOAT,                -- particulate matter ≤2.5µm
    carbon_monoxide FLOAT,      -- CO concentration
    ozone FLOAT,                -- O₃ concentration             -- C₈H₁₀ concentration
    lat FLOAT,                  -- latitude
    lon FLOAT,                  -- longitude
    source TEXT                 -- optional: API/source info
);
