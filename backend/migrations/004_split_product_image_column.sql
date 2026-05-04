-- Split the product image column into image_small and image.

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'products'
          AND column_name = 'image'
    ) AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'products'
          AND column_name = 'image_small'
    ) THEN
        EXECUTE 'ALTER TABLE products RENAME COLUMN image TO image_small';
    END IF;
END $$;

ALTER TABLE products
    ADD COLUMN IF NOT EXISTS image VARCHAR;
