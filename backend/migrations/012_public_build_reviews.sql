ALTER TABLE pc_builds
    ADD COLUMN IF NOT EXISTS is_public BOOLEAN NOT NULL DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS build_reviews (
    id SERIAL PRIMARY KEY,
    build_id INTEGER NOT NULL REFERENCES pc_builds(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_build_reviews_build_id ON build_reviews(build_id);
CREATE INDEX IF NOT EXISTS ix_build_reviews_user_id ON build_reviews(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_build_reviews_build_user ON build_reviews(build_id, user_id);