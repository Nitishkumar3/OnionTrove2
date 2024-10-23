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
    TorNetworkConsumedBandwidth FLOAT,
    torrelays INTEGER,
    torbridges INTEGER,
);


-------- Table "dorks" --------

CREATE TABLE dorks (
    sno SERIAL PRIMARY KEY,
    dork TEXT NOT NULL UNIQUE,          
    timesused INTEGER NOT NULL DEFAULT 0 CHECK (timesused >= 0),  
    lastused TIMESTAMP DEFAULT NULL,        
    dateadded TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  
    CONSTRAINT dork_not_empty CHECK (length(trim(dork)) > 0)
);

-- Add index for frequent searches and ordering
CREATE INDEX idx_dorks_dork ON dorks(dork);
CREATE INDEX idx_dorks_lastused ON dorks(lastused);
CREATE INDEX idx_dorks_timesused ON dorks(timesused);
