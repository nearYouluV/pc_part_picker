DO $$
BEGIN
	CREATE TYPE categoryenum AS ENUM ('cpu', 'gpu', 'motherboard', 'ram', 'storage', 'psu', 'cooler');
EXCEPTION
	WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS users (
	id SERIAL PRIMARY KEY,
	email VARCHAR UNIQUE,
	username VARCHAR NOT NULL UNIQUE,
	hashed_password VARCHAR NOT NULL,
	is_active BOOLEAN NOT NULL DEFAULT TRUE,
	is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
	refresh_token TEXT,
	refresh_token_expires TIMESTAMP WITH TIME ZONE,
	failed_login_attempts INTEGER NOT NULL DEFAULT 0,
	locked_until TIMESTAMP WITH TIME ZONE,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_id ON users(id);
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);

CREATE TABLE IF NOT EXISTS products (
	id SERIAL PRIMARY KEY,
	external_id INTEGER UNIQUE,
	name VARCHAR NOT NULL,
	price INTEGER NOT NULL,
	image VARCHAR,
	url VARCHAR,
	category categoryenum NOT NULL,
	subcategory VARCHAR,
	brand VARCHAR,
	other_features JSON
);

CREATE INDEX IF NOT EXISTS ix_products_external_id ON products(external_id);
CREATE INDEX IF NOT EXISTS ix_products_category ON products(category);

CREATE TABLE IF NOT EXISTS cpus (
	id SERIAL PRIMARY KEY,
	product_id INTEGER UNIQUE REFERENCES products(id) ON DELETE CASCADE,
	manufacturer VARCHAR NOT NULL,
	socket VARCHAR NOT NULL,
	cores INTEGER,
	threads INTEGER,
	base_clock DOUBLE PRECISION,
	boost_clock DOUBLE PRECISION,
	tdp INTEGER,
	memory_support VARCHAR,
	max_memory INTEGER,
	l3_cache INTEGER,
	pcie_support VARCHAR,
	performance_score INTEGER,
	graphics_model VARCHAR
);

CREATE TABLE IF NOT EXISTS gpus (
	id SERIAL PRIMARY KEY,
	product_id INTEGER UNIQUE REFERENCES products(id) ON DELETE CASCADE,
	vram INTEGER,
	memory_type VARCHAR,
	frequency INTEGER,
	max_resolution VARCHAR,
	performance INTEGER,
	recommended_power_supply INTEGER,
	power_connector VARCHAR
);

CREATE TABLE IF NOT EXISTS motherboards (
	id SERIAL PRIMARY KEY,
	product_id INTEGER UNIQUE REFERENCES products(id) ON DELETE CASCADE,
	socket VARCHAR NOT NULL,
	chipset VARCHAR,
	ram_type VARCHAR,
	max_ram INTEGER,
	memory_slots INTEGER,
	pcie_x1_slots INTEGER,
	m2_slots INTEGER,
	sata_ports INTEGER,
	total_channels INTEGER,
	form_factor VARCHAR,
	min_memory_frequency INTEGER,
	max_memory_frequency INTEGER,
	sys_fan INTEGER
);

CREATE TABLE IF NOT EXISTS rams (
	id SERIAL PRIMARY KEY,
	product_id INTEGER UNIQUE REFERENCES products(id) ON DELETE CASCADE,
	capacity INTEGER,
	modules_count INTEGER,
	memory_bandwidth INTEGER,
	ram_type VARCHAR,
	frequency INTEGER,
	cas_latency INTEGER,
	timings VARCHAR,
	voltage DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS psus (
	id SERIAL PRIMARY KEY,
	product_id INTEGER UNIQUE REFERENCES products(id) ON DELETE CASCADE,
	power INTEGER,
	certification VARCHAR,
	pfc VARCHAR,
	video_connector VARCHAR,
	modularity BOOLEAN
);

CREATE TABLE IF NOT EXISTS storage_specs (
	id SERIAL PRIMARY KEY,
	product_id INTEGER UNIQUE REFERENCES products(id) ON DELETE CASCADE,
	capacity INTEGER,
	interface VARCHAR,
	form_factor VARCHAR,
	memory_cells VARCHAR,
	read_speed INTEGER,
	write_speed INTEGER,
	rpm INTEGER
);

CREATE TABLE IF NOT EXISTS cooling_specs (
	id SERIAL PRIMARY KEY,
	product_id INTEGER UNIQUE REFERENCES products(id) ON DELETE CASCADE,
	cooling_type VARCHAR,
	tdp_support INTEGER,
	fan_size INTEGER,
	radiator_size INTEGER,
	noise_level INTEGER,
	tower_type VARCHAR,
	connection VARCHAR,
	fan_rpm VARCHAR,
	heatpipes INTEGER,
	airflow INTEGER,
	fan_count INTEGER,
	height INTEGER,
	socket_support VARCHAR[]
);
