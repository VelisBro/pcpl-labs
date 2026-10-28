"""РК-1: предметная область 18, запросы Б. Python 3.10+."""


class MusicalWork:
    """Произведение: ID, название, длительность и основной оркестр."""

    def __init__(self, id, title, duration_minutes, orchestra_id):
        self.id = id
        self.title = title
        self.duration_minutes = duration_minutes
        self.orchestra_id = orchestra_id


class Orchestra:
    """Оркестр: ID и название."""

    def __init__(self, id, name):
        self.id = id
        self.name = name


class WorkOrchestra:
    """Связь M:N: ID произведения и ID исполняющего его оркестра."""

    def __init__(self, work_id, orchestra_id):
        self.work_id = work_id
        self.orchestra_id = orchestra_id


def sample_data():
    """Учебное распределение репертуара, а не концертная афиша."""
    orchestras = [
        Orchestra(1, "Симфонический оркестр"),
        Orchestra(2, "Камерный оркестр"),
        Orchestra(3, "Филармонический оркестр"),
    ]
    works = [
        MusicalWork(1, "Вальс цветов", 8, 1),
        MusicalWork(2, "Танец эльфов", 3, 2),
        MusicalWork(3, "Танец рыцарей", 5, 1),
        MusicalWork(4, "Полет шмеля", 2, 3),
    ]
    links = [
        WorkOrchestra(1, 1),
        WorkOrchestra(1, 2),
        WorkOrchestra(2, 2),
        WorkOrchestra(3, 1),
        WorkOrchestra(4, 3),
    ]
    return works, orchestras, links


def query_b1(works, orchestras):
    """Б1: связь 1:N, сортировка по названию произведения."""
    one_to_many = [
        (work.title, orchestra.name)
        for work in works
        for orchestra in orchestras
        if work.orchestra_id == orchestra.id
    ]
    return sorted(one_to_many, key=lambda row: (row[0].casefold(), row[1]))


def query_b2(works, orchestras):
    """Б2: количество произведений по связи 1:N, по возрастанию."""
    counts = [
        (orchestra.name,
         sum(1 for work in works if work.orchestra_id == orchestra.id))
        for orchestra in orchestras
    ]
    # При равном количестве дополнительно сортируем по названию оркестра.
    return sorted(counts, key=lambda row: (row[1], row[0].casefold()))


def query_b3(works, orchestras, links):
    """Б3: названия на «ов» и оркестры через отдельную связь M:N."""
    return [
        (work.title, [
            orchestra.name
            for orchestra in orchestras
            if any(link.work_id == work.id
                   and link.orchestra_id == orchestra.id for link in links)
        ])
        for work in sorted(works, key=lambda work: work.title.casefold())
        if work.title.casefold().endswith("ов")
    ]


def main():
    works, orchestras, links = sample_data()
    print("РК-1. Вариант предметной области 18. Запросы Б")
    print("Б1. Произведения и основные оркестры, по названию произведения")
    for row in query_b1(works, orchestras):
        print(row)

    print("\nБ2. Оркестры и количество произведений, по возрастанию")
    for row in query_b2(works, orchestras):
        print(row)

    print("\nБ3. Произведения с окончанием 'ов' и их оркестры, связь M:N")
    for title, names in query_b3(works, orchestras, links):
        print(f"{title}: {', '.join(names) if names else 'нет оркестров'}")


if __name__ == "__main__":
    main()
