"""editable categories

Revision ID: 7157bcf0a8f8
Revises: 558e5b1a7af3
Create Date: 2026-09-17 22:40:15.418648

"""
from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7157bcf0a8f8'
down_revision: Union[str, Sequence[str], None] = '558e5b1a7af3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Прежние категории были строковым перечислением — переносим их в таблицу как стартовый набор.
LEGACY_CATEGORIES = [
    ("bar", "Бар", "pomegranate"),
    ("cafe", "Кофейня", "amber"),
    ("restaurant", "Ресторан", "plum"),
    ("culture", "Культура", "indigo"),
    ("activity", "Активность", "mint"),
    ("nature", "Природа", "olive"),
    ("other", "Другое", "slate"),
]


def upgrade() -> None:
    categories = op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=40), nullable=False),
        sa.Column("color", sa.String(length=16), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.bulk_insert(
        categories,
        [
            {
                "name": name,
                "color": color,
                "position": position,
                "created_at": datetime.now(timezone.utc),
            }
            for position, (_, name, color) in enumerate(LEGACY_CATEGORIES)
        ],
    )

    op.add_column("places", sa.Column("category_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_places_category_id"), "places", ["category_id"], unique=False)
    op.create_foreign_key(
        "fk_places_category_id", "places", "categories", ["category_id"], ["id"], ondelete="SET NULL"
    )

    for slug, name, _ in LEGACY_CATEGORIES:
        op.execute(
            sa.text(
                "UPDATE places SET category_id = (SELECT id FROM categories WHERE name = :name)"
                " WHERE category = :slug"
            ).bindparams(name=name, slug=slug)
        )

    op.drop_index(op.f("ix_places_category"), table_name="places")
    op.drop_column("places", "category")


def downgrade() -> None:
    op.add_column(
        "places",
        sa.Column("category", sa.VARCHAR(length=32), nullable=False, server_default="other"),
    )
    for slug, name, _ in LEGACY_CATEGORIES:
        op.execute(
            sa.text(
                "UPDATE places SET category = :slug"
                " WHERE category_id = (SELECT id FROM categories WHERE name = :name)"
            ).bindparams(name=name, slug=slug)
        )
    op.create_index(op.f("ix_places_category"), "places", ["category"], unique=False)
    op.drop_constraint("fk_places_category_id", "places", type_="foreignkey")
    op.drop_index(op.f("ix_places_category_id"), table_name="places")
    op.drop_column("places", "category_id")
    op.drop_table("categories")
