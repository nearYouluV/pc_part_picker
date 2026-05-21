CREATE TABLE IF NOT EXISTS build_suggestions (
    id SERIAL PRIMARY KEY,
    build_id INTEGER NOT NULL REFERENCES pc_builds(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR NOT NULL,
    suggested_product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    comment TEXT,
    status VARCHAR NOT NULL DEFAULT 'pending',
    applied_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    applied_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_build_suggestions_build_id ON build_suggestions(build_id);
CREATE INDEX IF NOT EXISTS ix_build_suggestions_user_id ON build_suggestions(user_id);
CREATE INDEX IF NOT EXISTS ix_build_suggestions_status ON build_suggestions(status);