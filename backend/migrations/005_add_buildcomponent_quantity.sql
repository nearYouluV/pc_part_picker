-- Add quantity column to build_components so users can select multiple pieces (e.g., RAM kits)
ALTER TABLE build_components
ADD COLUMN quantity INTEGER NOT NULL DEFAULT 1;
