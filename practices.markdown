# List of common development issues

- **Can't run unit tests because test database got too dirty/out-of-sync with
migrations.** Do as follows

    $ fab destroy_db_tables:is_test=True
    $ ./runtest
