"""standardize db conventions

Revision ID: 4f88e34f90c6
Revises: 1ac819f296cc
Create Date: 2016-04-12 17:49:41.968930

"""

# revision identifiers, used by Alembic.
revision = '4f88e34f90c6'
down_revision = '1ac819f296cc'
branch_labels = None
depends_on = None

import os
import sys

sys.path.append(os.getcwd())

from alembic import op
import sqlalchemy as sa


def upgrade():
    # General creator -> creator_id
    op.alter_column("librarians", "creator", new_column_name="creator_id")
    op.alter_column("roles", "creator", new_column_name="creator_id")
    op.alter_column("genres", "creator", new_column_name="creator_id")
    op.alter_column("books", "creator", new_column_name="creator_id")
    op.alter_column("book_companies", "creator", new_column_name="creator_id")
    op.alter_column("imprints", "creator", new_column_name="creator_id")
    op.alter_column("book_persons", "creator", new_column_name="creator_id")
    op.alter_column("book_participants", "creator", new_column_name="creator_id")
    op.alter_column("printers", "creator", new_column_name="creator_id")
    op.alter_column("pseudonyms", "creator", new_column_name="creator_id")

    # Genral last_modifier -> last_modifier_id
    op.alter_column("librarians", "last_modifier", new_column_name="last_modifier_id")
    op.alter_column("roles", "last_modifier", new_column_name="last_modifier_id")
    op.alter_column("genres", "last_modifier", new_column_name="last_modifier_id")
    op.alter_column("books", "last_modifier", new_column_name="last_modifier_id")
    op.alter_column("book_companies", "last_modifier", new_column_name="last_modifier_id")
    op.alter_column("imprints", "last_modifier", new_column_name="last_modifier_id")
    op.alter_column("book_persons", "last_modifier", new_column_name="last_modifier_id")
    op.alter_column("book_pariticipants", "last_modifier", new_column_name="last_modifier_id")
    op.alter_column("printers", "last_modifier", new_column_name="last_modifier_id")
    op.alter_column("pseudonyms", "last_modifier", new_column_name="last_modifier_id")

    # Modifications for Book table
    op.alter_column("books", "genre", new_column_name="genre_id")
    op.alter_column("books", "publisher", new_column_name="publisher_id")

    # Modifications for Imprint table
    op.alter_column("imprint", "mother_company", new_column_name="mother_company_id")
    op.alter_column("imprint", "imprint_company", new_column_name="imprint_company_id")

    # Rename awkwardly-named tables
    op.rename_table("book_persons", "contributors")
    op.rename_table("book_participants", "book_contributions")

    op.alter_column("book_contributions", "person_id", "contributor_id")


def downgrade():
    # General creator_id -> creator
    op.alter_column("librarians", "creator_id", new_column_name="creator")
    op.alter_column("roles", "creator_id", new_column_name="creator")
    op.alter_column("genres", "creator_id", new_column_name="creator")
    op.alter_column("books", "creator_id", new_column_name="creator")
    op.alter_column("book_companies", "creator_id", new_column_name="creator")
    op.alter_column("imprints", "creator_id", new_column_name="creator")
    op.alter_column("book_persons", "creator_id", new_column_name="creator")
    op.alter_column("book_participants", "creator_id", new_column_name="creator")
    op.alter_column("printers", "creator_id", new_column_name="creator")
    op.alter_column("pseudonyms", "creator_id", new_column_name="creator")

    # Genral last_modifier -> last_modifier_id
    op.alter_column("librarians", "last_modifier_id", new_column_name="last_modifier")
    op.alter_column("roles", "last_modifier_id", new_column_name="last_modifier")
    op.alter_column("genres", "last_modifier_id", new_column_name="last_modifier")
    op.alter_column("books", "last_modifier_id", new_column_name="last_modifier")
    op.alter_column("book_companies", "last_modifier_id", new_column_name="last_modifier")
    op.alter_column("imprints", "last_modifier_id", new_column_name="last_modifier")
    op.alter_column("book_persons", "last_modifier_id", new_column_name="last_modifier")
    op.alter_column("book_pariticipants", "last_modifier_id", new_column_name="last_modifier")
    op.alter_column("printers", "last_modifier_id", new_column_name="last_modifier")
    op.alter_column("pseudonyms", "last_modifier_id", new_column_name="last_modifier")

    # Modifications for Book table
    op.alter_column("books", "genre_id", new_column_name="genre")
    op.alter_column("books", "publisher_id", new_column_name="publisher")

    # Modifications for Imprint table
    op.alter_column("imprint", "mother_company_id", new_column_name="mother_company")
    op.alter_column("imprint", "imprint_company_id", new_column_name="imprint_company")

    # Rename awkwardly-named tables
    op.rename_table("contributors", "book_persons")
    op.rename_table("book_contributions", "book_participants")

    op.alter_column("book_participants", "contributor_id", "person_id")
