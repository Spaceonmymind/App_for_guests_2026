ACTIVITY_AWARD_RULES = {
    "Юный инвестор": ["participation", "winner"],
    "Инновационный ширпотреб": ["participation", "winner"],
    "Финансовый детектив": ["participation", "winner"],
    "Накопи на мечту": ["participation", "winner"],
    "Мамин инвестор": ["participation", "winner"],
    "Жажда власти": ["participation", "winner"],

    "ПС Мир": ["assembly"],
    "СБП": ["assembly"],
    "Блокчейн": ["assembly"],
    "3D-Secure": ["assembly"],

    "Квиз Мир Plat.Form": ["participation", "winner"],
    "Финтех-гуру": ["participation", "winner"],
    "Мир идей": ["participation", "winner"],
    "Прожарка резюме": ["participation"],
}


AWARD_OPTION_DEFINITIONS = {
    "participation": {
        "value": "participation",
        "label": "Участие",
        "points_source": "points_participation",
    },
    "winner": {
        "value": "winner",
        "label": "Победа",
        "points_source": "points_win",
    },
    "assembly": {
        "value": "assembly",
        "label": "Сбор",
        "points_source": "points_participation",
    },
}


def get_allowed_award_types(activity_name: str) -> list[str]:
    return ACTIVITY_AWARD_RULES.get(activity_name, [])


def get_award_options(activity_name: str) -> list[dict]:
    award_types = get_allowed_award_types(activity_name)

    result = []
    for award_type in award_types:
        option = AWARD_OPTION_DEFINITIONS.get(award_type)
        if option is not None:
            result.append(option)

    return result