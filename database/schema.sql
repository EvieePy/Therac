DO $$
BEGIN
    CREATE TYPE snowflake AS ENUM (
        'guild',
        'category',
        'channel',
        'role',
        'user',
        'member'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

DO $$
BEGIN
    CREATE TYPE rule AS ENUM (
        'channel_spam',
        'image_spam',
        'mention_spam',
        'url_spam',
        'general_spam'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

DO $$
BEGIN
    CREATE TYPE action AS ENUM (
        'notify',
        'warn',
        'timeout',
        'kick',
        'ban'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

CREATE TABLE IF NOT EXISTS rules(
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    guild_id BIGINT NOT NULL,
    type rule NOT NULL,
    action_type action NOT NULL,
    regex TEXT,
    rate INT,
    per INT,
    total INT,
    max_age INT
);

CREATE TABLE IF NOT EXISTS exceptions(
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rule_id BIGINT NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
    type snowflake NOT NULL,
    type_id BIGINT NOT NULL,
    UNIQUE (rule_id, type_id)
);

CREATE INDEX IF NOT EXISTS rules_guild_id_idx
    ON rules (guild_id);

CREATE INDEX IF NOT EXISTS rules_guild_type_idx
    ON rules (guild_id, type);

CREATE INDEX IF NOT EXISTS exceptions_rule_id_idx
    ON exceptions (rule_id);