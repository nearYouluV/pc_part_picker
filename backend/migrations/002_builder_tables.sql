CREATE TABLE IF NOT EXISTS pc_builds (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    budget INTEGER,
    goal VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_pc_builds_user_id ON pc_builds(user_id);

CREATE TABLE IF NOT EXISTS build_components (
    id SERIAL PRIMARY KEY,
    build_id INTEGER NOT NULL REFERENCES pc_builds(id) ON DELETE CASCADE,
    category VARCHAR NOT NULL,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_build_component_category UNIQUE (build_id, category)
);

CREATE INDEX IF NOT EXISTS ix_build_components_build_id ON build_components(build_id);
