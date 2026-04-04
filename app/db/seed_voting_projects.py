from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.voting_project import VotingProject

PROJECTS = [
    {
        "participant_name": "Кладиева Алёна",
        "project_name": "Дорожный Фактор",
        "description": "Телеметрический сервис для страхования, собирающий данные о стиле вождения и формирующий индивидуальные тарифы.",
        "photo_url": "/static/img/authors/dorozhnyy-faktor.png",
        "sort_order": 10,
    },
    {
        "participant_name": "Денисенко Софья",
        "project_name": "КлирЧек",
        "description": "Сервис для предварительного составления и согласования смет с оплатой со счета владельца бюджета только после сверки покупки с предварительным чеком.",
        "photo_url": "/static/img/authors/klirchek.png",
        "sort_order": 20,
    },
    {
        "participant_name": "Артемьев Богдан",
        "project_name": "УСПЕХ",
        "description": "Платформа для поиска профильной подработки и проектных задач для студентов, связывающая таланты и работодателей.",
        "photo_url": "/static/img/authors/uspeh.png",
        "sort_order": 30,
    },
    {
        "participant_name": "Ухачина Амина",
        "project_name": "QR-Корзина",
        "description": "AR/QR-интерфейс для формирования виртуальной корзины в зале и оплаты по СБП без кассы.",
        "photo_url": "/static/img/authors/qr-korzina.png",
        "sort_order": 40,
    },
    {
        "participant_name": "Слесаренко София",
        "project_name": "КорпЗакуп360",
        "description": "Облачный цикл закупок для государственных компаний.",
        "photo_url": "/static/img/authors/korpzakup360.png",
        "sort_order": 50,
    },
    {
        "participant_name": "Алексина Мария",
        "project_name": "БлагоДарю",
        "description": "Сервис оплаты через СБП со счета попечителя в пределах заранее заданных лимитов и ограничений.",
        "photo_url": "/static/img/authors/blagodaryu.png",
        "sort_order": 60,
    },
    {
        "participant_name": "Казарян Анна",
        "project_name": "Силуэт",
        "description": "Интеллектуальный сервис виртуальной примерки и точного подбора размеров одежды.",
        "photo_url": "/static/img/authors/siluet.png",
        "sort_order": 70,
    },
    {
        "participant_name": "Надыршина Лейсан",
        "project_name": "Смолл",
        "description": "Гибридная платформа для торговых центров с пунктами выдачи заказов.",
        "photo_url": "/static/img/authors/smoll.png",
        "sort_order": 80,
    },
    {
        "participant_name": "Давтян Гаяне",
        "project_name": "АгроИнвест",
        "description": "Цифровая платформа для привлечения инвестиций в сельское хозяйство.",
        "photo_url": "/static/img/authors/agroinvest.png",
        "sort_order": 90,
    },
    {
        "participant_name": "Киселёв Евгений",
        "project_name": "Цифровой иммунитет",
        "description": "Браузерное расширение для анализа страниц и предупреждения о мошенническом или манипулятивном контенте.",
        "photo_url": "/static/img/authors/cifrovoy-immunitet.png",
        "sort_order": 100,
    },
    {
        "participant_name": "Галактионов Иван",
        "project_name": "СБП-Экспресс",
        "description": "Интеграционная прослойка между «Мир» и СБП, позволяющая токенизировать способ оплаты СБП и совершать бесконтактные покупки.",
        "photo_url": "/static/img/authors/sbp-ekspress.png",
        "sort_order": 110,
    },
    {
        "participant_name": "Зайцева Екатерина",
        "project_name": "Солнышко",
        "description": "Цифровая платформа для школьных благотворительных ярмарок.",
        "photo_url": "/static/img/authors/solnyshko.png",
        "sort_order": 120,
    },
    {
        "participant_name": "Залевская Елизавета",
        "project_name": "Алгоритмическая должная добросовестность",
        "description": "Скоринговая платформа для эмитентов цифровых финансовых активов.",
        "photo_url": "/static/img/authors/algoritmicheskaya-dolzhnaya-dobrosovestnost.png",
        "sort_order": 130,
    },
    {
        "participant_name": "Пузырева Дарья",
        "project_name": "Оператор Цифровых Активов",
        "description": "Инфраструктурный мост между операторами информационных систем, создающий единое пространство для работы с ЦФА.",
        "photo_url": "/static/img/authors/operator-cifrovyh-aktivov.png",
        "sort_order": 140,
    },
    {
        "participant_name": "Макеева Анна",
        "project_name": "Моя МедКарта",
        "description": "Электронная карта пациента на Verifiable Credentials.",
        "photo_url": "/static/img/authors/moya-medkarta.png",
        "sort_order": 150,
    },
    {
        "participant_name": "Атарщикова Валерия",
        "project_name": "Ложка",
        "description": "Мобильный помощник по организации питания.",
        "photo_url": "/static/img/authors/lozhka.png",
        "sort_order": 160,
    },
    {
        "participant_name": "Куликов Руслан",
        "project_name": "Блокировки.Нет",
        "description": "Надстройка над RtP для анализа договоров и счетов и перманентного риск-скоринга платежей.",
        "photo_url": "/static/img/authors/blokirovki-net.png",
        "sort_order": 170,
    },
    {
        "participant_name": "Соловцева Алина",
        "project_name": "Кап-Кап ремонт",
        "description": "B2C-маркетплейс заявок на ремонт.",
        "photo_url": "/static/img/authors/kap-kap-remont.png",
        "sort_order": 180,
    },
    {
        "participant_name": "Иванов Илья",
        "project_name": "Центр регулярных платежей",
        "description": "Единый интерфейс для управления подписками и регулярными списаниями.",
        "photo_url": "/static/img/authors/centr-regulyarnyh-platezhey.png",
        "sort_order": 190,
    },
    {
        "participant_name": "Жакова Олеся",
        "project_name": "МИР Ритейла",
        "description": "Платформа персонализированных предложений по жизненным событиям с интеграцией API лояльности.",
        "photo_url": "/static/img/authors/mir-riteyla.png",
        "sort_order": 200,
    },
    {
        "participant_name": "Алиева Айдан",
        "project_name": "Вместе",
        "description": "Надстройка для маркетплейсов и интернет-магазинов, создающая общую корзину и совместное оформление заказа.",
        "photo_url": "/static/img/authors/vmeste.png",
        "sort_order": 210,
    },
]


def seed() -> None:
    with SessionLocal() as db:
        existing_names = set(
            db.scalars(select(VotingProject.project_name)).all()
        )

        created = 0

        for item in PROJECTS:
            if item["project_name"] in existing_names:
                continue

            db.add(
                VotingProject(
                    participant_name=item["participant_name"],
                    project_name=item["project_name"],
                    description=item["description"],
                    photo_url=item["photo_url"],
                    is_active=True,
                    sort_order=item["sort_order"],
                )
            )
            created += 1

        db.commit()
        print(f"Created voting projects: {created}")


if __name__ == "__main__":
    seed()