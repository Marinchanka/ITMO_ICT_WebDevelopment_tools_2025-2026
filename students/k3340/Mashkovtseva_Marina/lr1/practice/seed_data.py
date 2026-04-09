from connection import init_db, get_session
from models import Warrior, Profession, Skill, RaceType


def seed_database():
    # Создаем таблицы
    init_db()

    with next(get_session()) as session:
        # Добавляем профессии
        prof1 = Profession(id=1, title="Влиятельный человек", description="Эксперт по всем вопросам")
        prof2 = Profession(id=2, title="Дельфист-гребец", description="Уважаемый сотрудник")

        session.add_all([prof1, prof2])
        session.commit()

        # Добавляем умения
        skill1 = Skill(id=1, name="Купле-продажа компрессоров", description="")
        skill2 = Skill(id=2, name="Оценка имущества", description="")

        session.add_all([skill1, skill2])
        session.commit()

        # Добавляем воинов
        warrior1 = Warrior(
            id=1,
            race=RaceType.director,
            name="Мартынов Дмитрий",
            level=12,
            profession_id=1,
            skills=[skill1, skill2]
        )

        warrior2 = Warrior(
            id=2,
            race=RaceType.worker,
            name="Андрей Косякин",
            level=12,
            profession_id=2,
            skills=[]
        )

        session.add_all([warrior1, warrior2])
        session.commit()

        print("База данных успешно заполнена тестовыми данными!")


if __name__ == "__main__":
    seed_database()