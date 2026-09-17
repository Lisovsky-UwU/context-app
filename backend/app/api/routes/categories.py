from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import ACCENTS, Category, Place, User
from app.schemas.place import CategoryInput, CategoryPatch, CategoryPublic

router = APIRouter(prefix="/categories", tags=["categories"])


def _counts(db: Session) -> dict[int, int]:
    rows = db.execute(
        select(Place.category_id, func.count(Place.id))
        .where(Place.category_id.is_not(None))
        .group_by(Place.category_id)
    )
    return {category_id: count for category_id, count in rows}


def _public(category: Category, counts: dict[int, int]) -> CategoryPublic:
    return CategoryPublic(
        id=category.id,
        name=category.name,
        color=category.color,
        place_count=counts.get(category.id, 0),
    )


def _ordered(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.position, Category.id)))


def _check_color(color: str) -> str:
    if color not in ACCENTS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Такого цвета нет в палитре")
    return color


def _check_name(db: Session, name: str, category_id: int | None = None) -> str:
    name = name.strip()
    if not name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Впишите название категории")
    twin = db.scalar(select(Category).where(func.lower(Category.name) == name.lower()))
    if twin and twin.id != category_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Категория с таким названием уже есть")
    return name


@router.get("", response_model=list[CategoryPublic])
def list_categories(
    db: Session = Depends(get_db), user: User = Depends(current_user)
) -> list[CategoryPublic]:
    counts = _counts(db)
    return [_public(category, counts) for category in _ordered(db)]


@router.post("", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryInput, db: Session = Depends(get_db), user: User = Depends(current_user)
) -> CategoryPublic:
    last = db.scalar(select(func.max(Category.position)))
    category = Category(
        name=_check_name(db, payload.name),
        color=_check_color(payload.color),
        position=(last or 0) + 1,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return _public(category, {})


@router.patch("/{category_id}", response_model=CategoryPublic)
def update_category(
    category_id: int,
    payload: CategoryPatch,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> CategoryPublic:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Категория не найдена")

    fields = payload.model_dump(exclude_unset=True)
    if "name" in fields and fields["name"] is not None:
        category.name = _check_name(db, fields["name"], category.id)
    if "color" in fields and fields["color"] is not None:
        category.color = _check_color(fields["color"])
    if "position" in fields and fields["position"] is not None:
        category.position = fields["position"]

    db.commit()
    db.refresh(category)
    return _public(category, _counts(db))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    move_to: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> None:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Категория не найдена")

    places = list(db.scalars(select(Place).where(Place.category_id == category.id)))
    if places:
        if move_to is None:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"В категории {len(places)} мест. Выберите, куда их перенести",
            )
        if move_to == category.id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Выберите другую категорию")
        # move_to = 0 означает «оставить без категории»
        target = db.get(Category, move_to) if move_to else None
        if move_to and target is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Категория для переноса не найдена")
        for place in places:
            place.category_id = target.id if target else None

    db.delete(category)
    db.commit()
