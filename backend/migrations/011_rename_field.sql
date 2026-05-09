DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'chat_messages'
        AND column_name = 'metadata'
    ) THEN
        ALTER TABLE chat_messages
        RENAME COLUMN metadata TO metadata_json;
    END IF;
END
$$;