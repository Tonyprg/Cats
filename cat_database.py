import time
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session


class Base(DeclarativeBase):
    pass


class Cat(Base):

    __tablename__ = 'cat'

    name        = Column(String, primary_key=True, index=True)
    row         = Column(Integer,  default=16)
    col         = Column(Integer,  default=16)
    x           = Column(Integer,  default=0)
    y           = Column(Integer,  default=0)
    # я не нашел как преобразовать текущее время
    # time.time() во время формата sqlalchemy используя лишь модуль timе.
    # Поэтому время в базе храниться в виде числа типа Float
    time_adding = Column(Float,    default=time.time())
    coins       = Column(Integer,  default=0)
    state       = Column(String,   default='state')


engine = create_engine('sqlite:///cats.db')


def create():
    Base.metadata.create_all(bind=engine)


def read():
    res = {}
    with Session(autoflush=False, bind=engine) as db:
        for cat in db.query(Cat).all():
            res[cat.name] = {
                'name':        cat.name,
                'row':         cat.row,
                'col':         cat.col,
                'x':           cat.x,
                'y':           cat.y,
                'time_adding': cat.time_adding,
                'coins':       cat.coins,
                'state':       cat.state,
            }
    return res


def write(table):
    with Session(autoflush=False, bind=engine) as db:
        for key, value in table.items():
            row = db.query(Cat).filter(Cat.name == key).first()
            if row is None:
                row = Cat(name=key)
                db.add(row)

            row.row         = value['row']
            row.col         = value['col']
            row.x           = value['x']
            row.y           = value['y']
            row.time_adding = value['time_adding']
            row.coins       = value['coins']
            row.state       = value['state']

        db.commit()
        db.flush()
