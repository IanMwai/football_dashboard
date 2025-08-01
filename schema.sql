-- Static information about the teams
CREATE TABLE IF NOT EXISTS teams (
    team_id INT PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT,
    founded INT,
    stadium_name TEXT
);

-- Static information about players
CREATE TABLE IF NOT EXISTS players (
    player_id INT PRIMARY KEY,
    name TEXT NOT NULL,
    nationality TEXT,
    birthdate DATE
);

-- Static information about coaches
CREATE TABLE IF NOT EXISTS coaches (
    coach_id INT PRIMARY KEY,
    name TEXT NOT NULL,
    nationality TEXT
);

-- Records of which coach was with which team for a given season
CREATE TABLE IF NOT EXISTS coach_history (
    coach_id INT REFERENCES coaches(coach_id),
    team_id INT REFERENCES teams(team_id),
    season INT,
    PRIMARY KEY (coach_id, team_id, season)
);

-- Player statistics for a specific team and season
CREATE TABLE IF NOT EXISTS player_stats (
    player_id INT REFERENCES players(player_id),
    team_id INT REFERENCES teams(team_id),
    season INT,
    appearances INT,
    goals INT,
    assists INT,
    minutes_played INT,
    PRIMARY KEY (player_id, team_id, season)
);

-- Trophies won by players or coaches
CREATE TABLE IF NOT EXISTS trophies (
    trophy_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(player_id),
    coach_id INT REFERENCES coaches(coach_id),
    name TEXT NOT NULL,
    season INT,
    result TEXT,
    UNIQUE (player_id, coach_id, name, season)
);

-- Player transfers
CREATE TABLE IF NOT EXISTS transfers (
    transfer_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(player_id),
    from_team_id INT REFERENCES teams(team_id),
    to_team_id INT REFERENCES teams(team_id),
    transfer_fee NUMERIC,
    season INT,
    date DATE,
    UNIQUE (player_id, from_team_id, to_team_id, date)
);

-- Indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_player_name ON players(name);
CREATE INDEX IF NOT EXISTS idx_team_name ON teams(name);
CREATE INDEX IF NOT EXISTS idx_coach_name ON coaches(name);
CREATE INDEX IF NOT EXISTS idx_player_stats_season ON player_stats(player_id, season);
CREATE INDEX IF NOT EXISTS idx_transfers_player ON transfers(player_id);