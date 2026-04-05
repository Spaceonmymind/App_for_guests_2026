from app.repositories.master_poll_response_repository import MasterPollResponseRepository


POLL_STEPS = [
    {
        "index": "1",
        "title": "Инновации",
        "answers": [
            "А) Меня захватывает всё новое, я стремлюсь изучить это даже, если сначала освоить это кажется сложным",
            "Б) Если инновация понятна для меня и легко доступна, то я ей воспользуюсь, в ином случае быстро потеряю интерес",
            "В) Я очень избирательно отношусь к инновациям, предпочитаю сначала посмотреть как они используются другими, отзывы о них, обзоры по опыту их применения",
        ],
    },
    {
        "index": "2",
        "title": "Цифровые валюты и токенизация",
        "answers": [
            "А) С нетерпением жду понятных законных возможностей рассчитываться цифровыми валютами и понимаю суть цифровых активов",
            "Б) Не буду спешить, по мере необходимости буду осваивать и пользоваться цифровыми валютами и цифровыми активами",
            "В) Пока скорее мне непонятны возможности и безопасность этих видов финансовых инструментов",
        ],
    },
    {
        "index": "3",
        "title": "Искусственный интеллект и межагентные платежи",
        "answers": [
            "А) Да, это выглядит очень футуристично и сэкономит моё время",
            "Б) Если только на очень ограниченных сценариях (например, оплата подписок или парковки)",
            "В) Нет, я предпочту пока самостоятельно контролировать каждую транзакцию",
        ],
    },
    {
        "index": "4",
        "title": "Гиперперсонализация",
        "answers": [
            "А) Да, если мне это экономит деньги или время",
            "Б) Только на обезличенной основе, чтобы меня нельзя было идентифицировать, а просто сделать вывод банку или маркетплейсу как улучшить продукты для потребителя",
            "В) Нет, финансовые данные — это слишком личное",
        ],
    },
]


class MasterPollResultsService:
    def __init__(self, response_repo: MasterPollResponseRepository) -> None:
        self.response_repo = response_repo

    def _normalize(self, text: str) -> str:
        return " ".join(text.strip().lower().split())

    def build_results(self) -> list[dict]:
        distribution = self.response_repo.get_answer_distribution()
        all_responses = self.response_repo.get_all()
        total_respondents = len(all_responses)

        result = []

        for step in POLL_STEPS:
            counter = distribution.get(step["index"], {})

            # нормализуем ключи из БД
            normalized_counter = {
                self._normalize(k): v for k, v in counter.items()
            }

            total_answers = sum(normalized_counter.values())

            chart_items = []
            for answer in step["answers"]:
                normalized_answer = self._normalize(answer)

                count = normalized_counter.get(normalized_answer, 0)

                percent = round((count / total_answers) * 100) if total_answers > 0 else 0

                if answer.startswith("А)"):
                    short_label = "A"
                elif answer.startswith("Б)"):
                    short_label = "Б"
                else:
                    short_label = "В"

                chart_items.append(
                    {
                        "label": short_label,
                        "full_text": answer,
                        "count": count,
                        "percent": percent,
                    }
                )

            # строим круговую диаграмму
            segments = []
            current_percent = 0
            segment_colors = ["#C22FDE", "#7C4DFF", "#4FC3F7"]

            for index, item in enumerate(chart_items):
                percent = item["percent"]
                color = segment_colors[index % len(segment_colors)]

                start = current_percent
                end = current_percent + percent

                if percent > 0:
                    segments.append(f"{color} {start}% {end}%")

                current_percent = end

            chart_gradient = (
                "rgba(255,255,255,0.12) 0% 100%"
                if not segments
                else ", ".join(segments)
            )

            result.append(
                {
                    "title": step["title"],
                    "question_index": step["index"],
                    "total_answers": total_answers,
                    "total_respondents": total_respondents,
                    "items": chart_items,
                    "chart_gradient": chart_gradient,
                }
            )

        return result