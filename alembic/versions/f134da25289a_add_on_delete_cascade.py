"""add on delete cascade

Revision ID: f134da25289a
Revises: 703b37f58578
Create Date: 2016-12-23 05:17:54.558900

"""

# revision identifiers, used by Alembic.
revision = 'f134da25289a'
down_revision = '703b37f58578'
branch_labels = None
depends_on = None

import os
import sys

sys.path.append(os.getcwd())

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(
        "books", "publisher_id", sa.ForeignKey(
            "book_companies.id", name="book_book_company_fk1", ondelete="CASCADE"
        ), existing_type=sa.Integer
    )
    op.drop_constraint("book_book_company_fk1", "books", type_="foreignkey")
    op.create_foreign_key("book_book_company_fk1", "books", "publisher",
        ["publisher_id"], ["id"], ondelete="CASCADE")

    op.alter_column(
        "imprints", "mother_company_id", sa.ForeignKey(
            "book_companies.id", name="imprint_book_company_fk1",
            ondelete="CASCADE"
         ), existing_type=sa.Integer
    )
    op.alter_column(
        "imprints", "imprint_company_id", sa.ForeignKey(
            "book_companies.id", name="imprint_book_company_fk2",
            ondelete="CASCADE"
        ), existing_type=sa.Integer
    ) 

    op.alter_column(
        "book_contributions", "book_id", sa.ForeignKey(
            "books.id", name="book_participant_book_fk1", ondelete="CASCADE"
        ), existing_type=sa.Integer
    )
    op.alter_column(
        "book_contributions", "contributor_id", sa.ForeignKey(
            "contributors.id", name="book_participant_book_person_fk1",
            ondelete="CASCADE"
        ), existing_type=sa.Integer
    )
    # TODO: Rewrite this specifically to correct the typo in the name
    op.alter_column(
        "book_contributions", "role_id", sa.ForeignKey(
            "roles.id", name="book_pariticipant_role_fk1", ondelete="CASCADE"
        ), existing_type=sa.Integer
    )

    op.alter_column(
        "printers", "company_id", existing_type=sa.Integer, nullable=False,
        primary_key=True, kw=sa.ForeignKey(
            "book_companies.id", name="printer_book_company_fk1",
            ondelete="CASCADE"
        )
    )
    op.alter_column(
        "printers", "book_id", existing_type=sa.Integer, nullable=False,
        primary_key=True, kw=sa.ForeignKey(
            "books.id", name="printer_book_fk1", ondelete="CASCADE"
        )
    )

    op.alter_column(
        "pseudonyms", "person_id", existing_type=sa.Integer, nullable=False,
        primary_key=True, kw=sa.ForeignKey(
            "contributors.id", name="pseudonym_book_person_fk1",
            ondelete="CASCADE"
        )
    )
    op.alter_column(
        "pseudonyms", "book_id", existing_type=sa.Integer, nullable=False,
        primary_key=True, kw=sa.ForeignKey(
            "books.id", name="pseudonym_book_fk1", ondelete="CASCADE"
        )
    )

def downgrade():
    op.alter_column(
        "books", "publisher_id", sa.ForeignKey(
            "book_companies.id", name="book_book_company_fk1"
        ), existing_type=sa.Integer
    )

    op.alter_column(
        "imprints", "mother_company_id", sa.ForeignKey(
            "book_companies.id", name="imprint_book_company_fk1",
         ), existing_type=sa.Integer
    )
    op.alter_column(
        "imprints", "imprint_company_id", sa.ForeignKey(
            "book_companies.id", name="imprint_book_company_fk2",
        ), existing_type=sa.Integer
    ) 

    op.alter_column(
        "book_contributions", "book_id", sa.ForeignKey(
            "books.id", name="book_participant_book_fk1"
        ), existing_type=sa.Integer
    )
    op.alter_column(
        "book_contributions", "contributor_id", sa.ForeignKey(
            "contributors.id", name="book_participant_book_person_fk1",
        ), existing_type=sa.Integer
    )
    op.alter_column(
        "book_contributions", "role_id", sa.ForeignKey(
            "roles.id", name="book_pariticipant_role_fk1"
        ), existing_type=sa.Integer
    )

    op.alter_column(
        "printers", "company_id", existing_type=sa.Integer, nullable=False,
        primary_key=True, kw=sa.ForeignKey(
            "book_companies.id", name="printer_book_company_fk1",
        )
    )
    op.alter_column(
        "printers", "book_id", existing_type=sa.Integer, nullalbe=False,
        primary_key=True, kw=sa.ForeignKey(
            "books.id", name="printer_book_fk1"
        )
    )

    op.alter_column(
        "pseudonyms", "person_id", existing_type=sa.Integer, nullable=True,
        primary_key=True, kw=sa.ForeignKey(
            "contributors.id", name="pseudonym_book_person_fk1",
        )
    )
    op.alter_column(
        "pseudonyms", "book_id", existing_type=sa.Integer, nullable=True,
        primary_key=True, kw=sa.ForeignKey(
            "books.id", name="pseudonym_book_fk1"
        )
    )
