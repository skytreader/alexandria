# List of common development issues

- **Can't run unit tests because test database got too dirty/out-of-sync with
migrations.** Do as follows

    $ fab destroy_db_tables:is_test=True
    $ ./runtest

- **Creating a new migration.** Since migrations may not always be reversible
and since they may (potentially) ruin the database, use `fab clone_database`
before creating or running a new migration.
