from datetime import date, time

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.program_session import ProgramSession

SESSIONS = [
    # 9 апреля — Главный зал форума
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "main",
        "hall_name": "Главный зал форума",
        "title": "Регистрация участников, кофе-брейк, интерактивы",
        "start_time": time(9, 30),
        "end_time": time(11, 30),
        "sort_order": 10,
    },
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "main",
        "hall_name": "Главный зал форума",
        "title": "Открытие Молодежного форума платежных технологий",
        "start_time": time(11, 30),
        "end_time": time(11, 35),
        "sort_order": 20,
    },
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "main",
        "hall_name": "Главный зал форума",
        "title": "Презентация и защита идей творческого трека",
        "start_time": time(11, 35),
        "end_time": time(13, 40),
        "sort_order": 30,
    },
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "main",
        "hall_name": "Главный зал форума",
        "title": "Кофе-брейк, интерактивы",
        "start_time": time(13, 40),
        "end_time": time(15, 0),
        "sort_order": 40,
    },
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "main",
        "hall_name": "Главный зал форума",
        "title": "Презентация и защита идей проектов творческого трека",
        "start_time": time(15, 0),
        "end_time": time(17, 0),
        "sort_order": 50,
    },
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "main",
        "hall_name": "Главный зал форума",
        "title": "Впечатления жюри",
        "start_time": time(17, 0),
        "end_time": time(17, 10),
        "sort_order": 60,
    },
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "main",
        "hall_name": "Главный зал форума",
        "title": "Подведение итогов, объявление финалистов, приз зрительских симпатий",
        "start_time": time(17, 10),
        "end_time": time(18, 0),
        "sort_order": 70,
    },

    # 10 апреля — Главный зал форума
    {
        "session_date": date(2026, 4, 10),
        "hall_code": "main",
        "hall_name": "Главный зал форума",
        "title": "Регистрация участников, кофе-брейк, интерактивы",
        "start_time": time(11, 0),
        "end_time": time(13, 0),
        "sort_order": 10,
    },
    {
        "session_date": date(2026, 4, 10),
        "hall_code": "main",
        "hall_name": "Главный зал форума",
        "title": "Открытие финала Молодежного форума платежных технологий",
        "start_time": time(13, 0),
        "end_time": time(13, 10),
        "sort_order": 20,
    },
    {
        "session_date": date(2026, 4, 10),
        "hall_code": "main",
        "hall_name": "Главный зал форума",
        "title": "Презентация и защита идей проектов финалистов",
        "start_time": time(13, 10),
        "end_time": time(14, 20),
        "sort_order": 30,
    },
    {
        "session_date": date(2026, 4, 10),
        "hall_code": "main",
        "hall_name": "Главный зал форума",
        "title": "Впечатления жюри",
        "start_time": time(14, 20),
        "end_time": time(14, 25),
        "sort_order": 40,
    },
    {
        "session_date": date(2026, 4, 10),
        "hall_code": "main",
        "hall_name": "Главный зал форума",
        "title": "Награждение победителей",
        "start_time": time(14, 25),
        "end_time": time(15, 0),
        "sort_order": 50,
    },
    # 9 апреля — Зал финансовых игр
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "financial-games",
        "hall_name": "Зал финансовых игр",
        "title": "Открытие трека финансовые игры",
        "start_time": time(10, 0),
        "end_time": time(10, 10),
        "sort_order": 10,
    },
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "financial-games",
        "hall_name": "Зал финансовых игр",
        "title": "Финансовые игры 1-2 раунды",
        "start_time": time(10, 10),
        "end_time": time(11, 10),
        "sort_order": 20,
    },
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "financial-games",
        "hall_name": "Зал финансовых игр",
        "title": "Финансовые игры 3-4 раунды",
        "start_time": time(13, 50),
        "end_time": time(14, 50),
        "sort_order": 30,
    },

    # 10 апреля — Зал финансовых игр
    {
        "session_date": date(2026, 4, 10),
        "hall_code": "financial-games",
        "hall_name": "Зал финансовых игр",
        "title": "Финансовые игры 5-6 раунды",
        "start_time": time(11, 40),
        "end_time": time(12, 40),
        "sort_order": 10,
    },

    # 9 апреля — Бренд-зона, Секция 1
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "brand-zone",
        "hall_name": "Бренд-зона",
        "title": "Финтех-гуру",
        "section_title": "Секция 1",
        "start_time": time(9, 30),
        "end_time": time(11, 30),
        "sort_order": 10,
    },
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "brand-zone",
        "hall_name": "Бренд-зона",
        "title": "Финтех-гуру",
        "section_title": "Секция 1",
        "start_time": time(13, 40),
        "end_time": time(14, 55),
        "sort_order": 20,
    },

    # 9 апреля — Бренд-зона, Секция 2
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "brand-zone",
        "hall_name": "Бренд-зона",
        "title": "Мир идей",
        "section_title": "Секция 2",
        "start_time": time(9, 30),
        "end_time": time(11, 30),
        "sort_order": 30,
    },
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "brand-zone",
        "hall_name": "Бренд-зона",
        "title": "Мир идей",
        "section_title": "Секция 2",
        "start_time": time(13, 40),
        "end_time": time(14, 55),
        "sort_order": 40,
    },

    # 9 апреля — Бренд-зона, Секция 3
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "brand-zone",
        "hall_name": "Бренд-зона",
        "title": "Диалог о современных технологиях Гашникова Григория с Правкиным Кириллом",
        "section_title": "Секция 3",
        "start_time": time(10, 30),
        "end_time": time(11, 0),
        "sort_order": 50,
    },
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "brand-zone",
        "hall_name": "Бренд-зона",
        "title": "Награждение КМБ Лайт",
        "section_title": "Секция 3",
        "start_time": time(11, 0),
        "end_time": time(11, 15),
        "sort_order": 60,
    },
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "brand-zone",
        "hall_name": "Бренд-зона",
        "title": "Презентация ИФТП, КМБ",
        "section_title": "Секция 3",
        "start_time": time(13, 50),
        "end_time": time(14, 10),
        "sort_order": 70,
    },
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "brand-zone",
        "hall_name": "Бренд-зона",
        "title": "Квиз Мир платформ",
        "section_title": "Секция 3",
        "start_time": time(14, 10),
        "end_time": time(14, 55),
        "sort_order": 80,
    },

    {
        "session_date": date(2026, 4, 9),
        "hall_code": "brand-zone",
        "hall_name": "Бренд-зона",
        "title": "Награждение МГБ",
        "section_title": "Секция 3",
        "start_time": time(18, 0),
        "end_time": time(18, 0),
        "sort_order": 90,
    },

    # 9 апреля — Бренд-зона, Секция 4
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "brand-zone",
        "hall_name": "Бренд-зона",
        "title": "Карьерные консультации",
        "section_title": "Секция 4",
        "start_time": time(13, 50),
        "end_time": time(14, 55),
        "sort_order": 100,
    },

    # 9 апреля — Зал конструктора транзакций
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "transaction-constructor",
        "hall_name": "Зал конструктора транзакций",
        "title": "Сбор транзакций",
        "start_time": time(9, 30),
        "end_time": time(11, 30),
        "sort_order": 10,
    },
    {
        "session_date": date(2026, 4, 9),
        "hall_code": "transaction-constructor",
        "hall_name": "Зал конструктора транзакций",
        "title": "Сбор транзакций",
        "start_time": time(13, 40),
        "end_time": time(15, 0),
        "sort_order": 20,
    },


    # 10 апреля — Зал конструктора транзакций
    {
        "session_date": date(2026, 4, 10),
        "hall_code": "transaction-constructor",
        "hall_name": "Зал конструктора транзакций",
        "title": "Сбор транзакций",
        "start_time": time(11, 0),
        "end_time": time(13, 0),
        "sort_order": 10,
    },
]




def seed() -> None:
    with SessionLocal() as db:
        existing_keys = set(
            db.execute(
                select(
                    ProgramSession.session_date,
                    ProgramSession.hall_code,
                    ProgramSession.start_time,
                    ProgramSession.title,
                    ProgramSession.section_title,
                )
            ).all()
        )

        created = 0

        for item in SESSIONS:
            key = (
                item["session_date"],
                item["hall_code"],
                item["start_time"],
                item["title"],
                item.get("section_title"),
            )
            if key in existing_keys:
                continue

            db.add(
                ProgramSession(
                    session_date=item["session_date"],
                    hall_code=item["hall_code"],
                    hall_name=item["hall_name"],
                    title=item["title"],
                    section_title=item.get("section_title"),
                    start_time=item["start_time"],
                    end_time=item["end_time"],
                    sort_order=item["sort_order"],
                )
            )
            created += 1

        db.commit()
        print(f"Created program sessions: {created}")


if __name__ == "__main__":
    seed()