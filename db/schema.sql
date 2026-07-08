-- ============================================================
-- Statose Football Data Platform — PostgreSQL Schema
-- ============================================================
-- Run this against a fresh database, e.g.:
--   psql -U postgres -d statose -f schema.sql
-- ============================================================


-- ============================================================
-- 1. IDENTITY LAYER
-- ============================================================

CREATE TABLE countries (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    iso2        CHAR(2) UNIQUE,
    iso3        CHAR(3) UNIQUE
);

CREATE TABLE teams (
    id              SERIAL PRIMARY KEY,
    fotmob_id       INTEGER UNIQUE,
    name            VARCHAR(150) NOT NULL,
    short_name      VARCHAR(50),
    country_id      INTEGER NOT NULL REFERENCES countries(id),
    foundation_year INTEGER,
    logo_url        VARCHAR(500),
    stadium_name    VARCHAR(150),
    created_at      TIMESTAMP NOT NULL DEFAULT now(),
    updated_at      TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_teams_country_id ON teams(country_id);


CREATE TABLE players (
    id                  SERIAL PRIMARY KEY,
    full_name           VARCHAR(150) NOT NULL,
    date_of_birth       DATE,
    nationality_id      INTEGER REFERENCES countries(id),
    primary_position    VARCHAR(30),
    secondary_position  VARCHAR(30),
    preferred_foot      VARCHAR(10),
    height_cm           INTEGER,
    weight_kg           DECIMAL(5,2),
    created_at          TIMESTAMP NOT NULL DEFAULT now(),
    updated_at          TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_players_nationality_id ON players(nationality_id);


CREATE TABLE competitions (
    id                  SERIAL PRIMARY KEY,
    country_id          INTEGER NOT NULL REFERENCES countries(id),
    gradient_league_id  INTEGER,
    fotmob_league_id    INTEGER,
    name                VARCHAR(150) NOT NULL,
    logo_url            VARCHAR(500),
    competition_type    VARCHAR(30),  -- 'league', 'cup', 'international', etc.
    gender              VARCHAR(10)
);

CREATE INDEX idx_competitions_country_id ON competitions(country_id);


-- ============================================================
-- 2. CONTEXT LAYER
-- ============================================================

CREATE TABLE seasons (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(20) NOT NULL UNIQUE,  -- e.g. '2024/25'
    start_date  DATE,
    end_date    DATE,
    is_current  BOOLEAN NOT NULL DEFAULT false,
    created_at  TIMESTAMP NOT NULL DEFAULT now()
);


CREATE TABLE player_seasons (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL REFERENCES players(id),
    team_id         INTEGER NOT NULL REFERENCES teams(id),
    season_id       INTEGER NOT NULL REFERENCES seasons(id),
    shirt_number    INTEGER,
    position        VARCHAR(30),  -- position as played THIS season (can differ from player's career default)
    appearances     INTEGER,
    starts          INTEGER,
    minutes         INTEGER,
    goals           INTEGER,
    assists         INTEGER,
    yellow_cards    INTEGER,
    red_cards       INTEGER,
    created_at      TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT uq_player_team_season UNIQUE (player_id, team_id, season_id)
);

CREATE INDEX idx_player_seasons_player_id ON player_seasons(player_id);
CREATE INDEX idx_player_seasons_team_id ON player_seasons(team_id);
CREATE INDEX idx_player_seasons_season_id ON player_seasons(season_id);


CREATE TABLE player_season_competitions (
    id                  SERIAL PRIMARY KEY,
    player_season_id    INTEGER NOT NULL REFERENCES player_seasons(id),
    competition_id      INTEGER NOT NULL REFERENCES competitions(id),
    appearances         INTEGER,
    starts              INTEGER,
    minutes             INTEGER,
    goals               INTEGER,
    assists             INTEGER,

    CONSTRAINT uq_player_season_competition UNIQUE (player_season_id, competition_id)
);

CREATE INDEX idx_psc_player_season_id ON player_season_competitions(player_season_id);
CREATE INDEX idx_psc_competition_id ON player_season_competitions(competition_id);


-- ============================================================
-- 3. METRICS SYSTEM (PERFORMANCE LAYER)
-- ============================================================

CREATE TABLE metrics (
    id              SERIAL PRIMARY KEY,
    provider        VARCHAR(50) NOT NULL,   -- 'gradient', 'scoutlab', 'fotmob'
    metric_key      VARCHAR(100) NOT NULL,  -- raw key from provider API
    metric_name     VARCHAR(150) NOT NULL,  -- human-readable display name
    group_name      VARCHAR(50),            -- 'Passing', 'Shooting', etc.
    stat_type       VARCHAR(20),            -- 'count', 'percentage', 'rate'
    is_per90        BOOLEAN NOT NULL DEFAULT false,
    is_percentage   BOOLEAN NOT NULL DEFAULT false,
    is_negative     BOOLEAN NOT NULL DEFAULT false,  -- true if lower is better (e.g. miscontrols)
    created_at      TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT uq_provider_metric_key UNIQUE (provider, metric_key)
);


CREATE TABLE player_metrics (
    id                  SERIAL PRIMARY KEY,
    player_season_id    INTEGER NOT NULL REFERENCES player_seasons(id),
    metric_id           INTEGER NOT NULL REFERENCES metrics(id),
    value               DECIMAL(10,3),
    per90               DECIMAL(10,3),
    percentile          DECIMAL(5,2),  -- 0.00 to 100.00
    percentile_per90    DECIMAL(5,2),
    created_at          TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT uq_player_season_metric UNIQUE (player_season_id, metric_id)
);

CREATE INDEX idx_player_metrics_metric_id ON player_metrics(metric_id);
-- (player_season_id, metric_id) lookups are already covered by the unique constraint above


-- ============================================================
-- 4. FUTURE EXTENSIONS — see schema design doc section 8
-- ============================================================
-- The following are NOT created by this script. They're noted here
-- as a reminder of where they'll plug into the existing schema:
--
--   team_seasons              -> team_id, season_id, aggregate team stats
--   team_metrics              -> mirrors player_metrics but keyed on team_season_id
--   matches                   -> home_team_id, away_team_id, competition_id, season_id, date
--   match_player_stats        -> match_id, player_id, per-game version of player_metrics
--   transfers                 -> player_id, from_team_id, to_team_id, transfer_date, fee, transfer_type
--
-- These are intentionally left out of v1 to keep the initial schema
-- shippable. See the design doc for how each will attach to the
-- existing tables without requiring changes to what's built here.
-- ============================================================
