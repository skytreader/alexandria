"""make constraint names follow as specified in models.py

Revision ID: 09a48c35766b
Revises: f134da25289a
Create Date: 2016-12-27 05:29:00.580632

"""

# revision identifiers, used by Alembic.
revision = '09a48c35766b'
down_revision = 'f134da25289a'
branch_labels = None
depends_on = None

import os
import sys

sys.path.append(os.getcwd())

from alembic import op
import sqlalchemy as sa


IDX_CONSTRAINT_NAME = 0
IDX_TABLE = 1
IDX_PARENT_TABLE = 2
IDX_TABLE_COL = 3
# constraint name, table, parent table, table col
COL_CONS = [
    ("book_company_fk1", "books", "book_companies", "publisher_id"),
    ("imprint_company_fk1", "imprints", "book_companies", "mother_company_id"),
    ("imprint_company_fk2", "imprints", "book_companies", "imprint_company_id"),
    ("book_contributions_ibfk_1", "book_contributions", "books", "book_id"),
    ("book_contributions_ibfk_2", "book_contributions", "contributors", "contributor_id"),
    ("book_contributions_ibfk_3", "book_contributions", "roles", "role_id"),
    ("printers_ibfk_1", "printers", "book_companies", "company_id"),
    ("printers_ibfk_2", "printers", "books", "book_id"),
    ("pseudonyms_ibfk_1", "pseudonyms", "contributors", "person_id"),
    ("pseudonyms_ibfk_2", "pseudonyms", "books", "book_id")
]

NEW_NAMES = {
    "book_company_fk1": "book_book_company_fk1",
    "imprint_company_fk1": "imprint_book_company_fk1",
    "imprint_company_fk2": "imprint_book_company_fk2",
    "book_contributions_ibfk_1": "book_participant_book_fk1",
    "book_contributions_ibfk_2": "book_participant_book_person_fk1",
    "book_contributions_ibfk_3": "book_participant_role_fk1",
    "printers_ibfk_1": "printer_book_company_fk1",
    "printers_ibfk_2": "pritners_book_fk1",
    "pseudonyms_ibfk_1": "pseudonym_book_person_fk1",
    "pseudonyms_ibfk_2": "pseudonym_book_fk1"
}

def upgrade():
    for cc in COL_CONS:
        old_constraint_name = cc[IDX_CONSTRAINT_NAME]
        op.drop_constraint(
            old_constraint_name, cc[IDX_TABLE], type_="foreignkey"
        )
        op.create_foreign_key(
            NEW_NAMES[old_constraint_name], cc[IDX_TABLE], cc[IDX_PARENT_TABLE],
            [cc[IDX_TABLE_COL]], ["id"], ondelete="CASCADE"
        )


def downgrade():
    for cc in COL_CONS:
        op.drop_constraint(
            NEW_NAMES[cc[IDX_CONSTRAINT_NAME]], cc[IDX_TABLE], type_="foreignkey"
        )
        op.create_foreign_key(
            cc[IDX_CONSTRAINT_NAME], cc[IDX_TABLE], cc[IDX_PARENT_TABLE],
            [cc[IDX_TABLE_COL]], ["id"], ondelete="CASCADE"
        )
