def get_admin_award_options(activity_name: str) -> list[dict]:
    financial_games = {
        "Юный инвестор",
        "Инновационный ширпотреб",
        "Финансовый детектив",
        "Накопи на мечту",
        "Мамин инвестор",
        "Жажда власти",
        "Квиз Мир Plat.Form",
        "Финтех-гуру",
        "Мир идей",
    }

    constructors = {
        "ПС Мир",
        "СБП",
        "Блокчейн",
        "3D-Secure",
    }

    participation_only = {
        "Прожарка резюме",
        "Мастер-опрос",
        "Голосование за лучший проект",
    }

    if activity_name in financial_games:
        return [
            {"value": "participation", "label": "Участие", "points_source": "points_participation"},
            {"value": "winner", "label": "Победа", "points_source": "points_win"},
        ]

    if activity_name in constructors:
        return [
            {"value": "assembly", "label": "Сбор", "points_source": "points_participation"},
        ]

    if activity_name in participation_only:
        return [
            {"value": "participation", "label": "Участие", "points_source": "points_participation"},
        ]

    return []