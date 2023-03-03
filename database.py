from sqlalchemy import create_engine, Column, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship

database_uri = "sqlite:///database.db"
engine = create_engine(database_uri, echo=True)


class Base(DeclarativeBase):
    pass


class VkUser(Base):
    __tablename__ = "vk_user"

    user_id = Column(Integer, primary_key=True)
    sex = Column(Integer, nullable=True)
    age = Column(Integer, nullable=True)
    city_id = Column(Integer, nullable=True)
    relation = Column(Integer, nullable=True)
    couples = relationship("Couple", back_populates="vk_user")


class Couple(Base):
    __tablename__ = "couple"
    id = Column(Integer, primary_key=True)
    couple_user_id = Column(Integer)
    vk_user_id = Column(Integer, ForeignKey("vk_user.user_id"))
    vk_user = relationship("VkUser", back_populates="couples")


Base.metadata.create_all(bind=engine)
engine = create_engine(database_uri, echo=False)
Session = sessionmaker(autoflush=False, bind=engine)


def save_vk_user(user_id, sex, age, city_id, relation):
    if find_vk_user_by_id(user_id) is None:
        with Session(autoflush=False, bind=engine) as db:
            vk_user = VkUser(user_id=user_id, sex=sex, age=age, city_id=city_id, relation=relation)
            db.add(vk_user)
            db.commit()


def get_users():
    with Session(autoflush=False, bind=engine) as db:
        return db.query(VkUser).all()


def find_vk_user_by_id(user_id):
    with Session(autoflush=False, bind=engine) as db:
        return db.query(VkUser).filter(VkUser.user_id == user_id).first()


def find_history_couples_id_by_user_id(user_id):
    with Session(autoflush=False, bind=engine) as db:
        user = db.query(VkUser).filter(VkUser.user_id == user_id).first()
        return [i.couple_user_id for i in user.couples]


def add_couple_in_history(user_id, couple_user_id):
    with Session(autoflush=False, bind=engine) as db:
        couple = Couple(couple_user_id=couple_user_id, vk_user_id=user_id)
        db.add(couple)
        db.commit()


def find_couple_for_vk_user(user_id):
    user = find_vk_user_by_id(user_id)
    couple = None
    for other_user in get_users():
        if other_user.sex != user.sex and other_user.city_id == user.city_id and (
                other_user.relation in [1, 5, 6] or other_user.relation is None):
            couple = other_user
            if couple.user_id in find_history_couples_id_by_user_id(user_id):
                couple = None
                continue
            else:
                add_couple_in_history(user_id, couple.user_id)
                break
    return couple
