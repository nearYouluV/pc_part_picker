-- Migration: Add source column to build_components
ALTER TABLE build_components
ADD COLUMN source VARCHAR(16) NOT NULL DEFAULT 'user';

-- If your DB requires setting existing rows explicitly, default will apply.