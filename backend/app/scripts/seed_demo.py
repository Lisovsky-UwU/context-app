"""Наполняет базу примерами мест — только для разработки.

    uv run python -m app.scripts.seed_demo
"""

from datetime import date, timedelta

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Category, Place, User, Visit, VisitStatus

DEMO_PLACES = [
    ("Бар «Стрелка»", "Бар", "Москва, Берсеневская набережная, 14с5", 55.7415, 37.6085,
     "Терраса с видом на Храм Христа Спасителя. Идём в тёплый вечер, столик бронировать заранее."),
    ("Кофейня «Филин»", "Кофейня", "Москва, Покровка, 27", 55.7602, 37.6491,
     "Обжаривают сами, есть фильтр на вынос. Работает с восьми утра."),
    ("Музей русского импрессионизма", "Культура", "Москва, Ленинградский проспект, 15с11", 55.7876, 37.5638,
     "Небольшой музей на территории бывшей фабрики «Большевик». По четвергам открыт до девяти."),
    ("Лапшичная «Ку»", "Ресторан", "Москва, Большая Никитская, 22/2", 55.7566, 37.6003,
     "Рамен и гёдза, очередь после семи вечера."),
    ("Скалодром «Скала-Сити»", "Активность", "Москва, Автозаводская, 18", 55.7062, 37.6572,
     "Трассы для новичков есть, обувь напрокат. Берём с собой воду."),
    ("Ботанический сад МГУ «Аптекарский огород»", "Природа", "Москва, проспект Мира, 26с1", 55.7767, 37.6326,
     "Оранжерея с пальмами, зимой особенно спасает. Билеты только на сайте."),
]


def main() -> None:
    with SessionLocal() as db:
        author = db.scalar(select(User).order_by(User.id))
        categories = {category.name: category.id for category in db.scalars(select(Category))}
        created = 0
        for title, category, address, lat, lon, description in DEMO_PLACES:
            if db.scalar(select(Place).where(Place.title == title)):
                continue
            db.add(
                Place(
                    title=title,
                    category_id=categories.get(category),
                    address=address,
                    lat=lat,
                    lon=lon,
                    description=description,
                    created_by_id=author.id if author else None,
                )
            )
            created += 1
        db.commit()

        museum = db.scalar(select(Place).where(Place.title.like("Музей%")))
        if museum and not db.scalar(select(Visit).where(Visit.place_id == museum.id)):
            db.add(
                Visit(
                    place_id=museum.id,
                    scheduled_date=date.today() - timedelta(days=12),
                    status=VisitStatus.done,
                    note="Успели на экскурсию",
                    created_by_id=author.id if author else None,
                )
            )
            db.commit()
        print(f"Добавлено мест: {created}")


if __name__ == "__main__":
    main()
