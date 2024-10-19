CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
);
CREATE TABLE TorMetricsMetaData (
    key TEXT PRIMARY KEY,
    value TIMESTAMP
);

CREATE TABLE TorMetrics (
    date DATE NOT NULL UNIQUE,
    TorRelayUsers INTEGER,
    TorBridgeUsers INTEGER,
    OnionSites INTEGER,
    OnionServiceBandwidth FLOAT,
    TorNetworkAdvertisedBandwidth FLOAT,
    TorNetworkConsumedBandwidth FLOAT
);

CREATE TABLE dorks (
    sno SERIAL PRIMARY KEY,          
    dork TEXT NOT NULL,              
    timesused INTEGER DEFAULT 0,     
    lastused TIMESTAMP,              
    dateadded TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);