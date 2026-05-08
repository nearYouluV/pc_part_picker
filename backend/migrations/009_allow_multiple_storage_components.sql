-- Allow multiple components in the same category for a build when product_id differs.
-- This enables combinations like SSD + HDD while keeping duplicate rows for the same product prevented.

ALTER TABLE build_components
DROP CONSTRAINT IF EXISTS uq_build_component_category;

ALTER TABLE build_components
ADD CONSTRAINT uq_build_component_category_product UNIQUE (build_id, category, product_id);
