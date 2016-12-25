IDX_CONSTRAINT_NAME = 0
IDX_TABLE = 1
IDX_PARENT_TABLE = 2
IDX_TABLE_COL = 3
IDX_PARENT_TABLE_COL = 4
# constraint name, table, parent table, table col, parent table col
COL_CONS = [
    ("book_book_company_fk1", "books", "publisher", "publisher_id", "id"),
    ("imprint_book_company_fk1", "imprints", "book_companies", "mother_company_id", "id"),
    ("imprint_book_company_fk2", "imprints", "book_companies", "imprint_company_id", "id"),
    ("book_participant_book_fk1", "book_contributions", "books", "book_id", "id"),
    ("book_participant_book_person_fk1", "book_contributions", "contributors", "contributor_id", "id"),
    ("printer_book_company_fk1", "printers", "book_companies", "company_id", "id"),
    ("printer_book_fk1", "printers", "books", "book_id", "id"),
    ("pseudonym_book_person_fk1", "pseudonyms", "contributors", "person_id", "id"),
    ("pseudonym_book_fk1", "pseudonyms", "books", "book_id", "id")
]
