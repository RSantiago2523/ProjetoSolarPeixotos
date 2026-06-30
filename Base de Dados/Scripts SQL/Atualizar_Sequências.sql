DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE column_default LIKE 'nextval%'
    LOOP
        EXECUTE format(
            'SELECT setval(pg_get_serial_sequence(''%s'', ''%s''), COALESCE(MAX(%s),1)) FROM %s;',
            r.table_name, r.column_name, r.column_name, r.table_name
        );
    END LOOP;
END $$;