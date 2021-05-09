from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, aliased

Base = declarative_base()

class ConnectionConfig:
    def __init__(self):
        self.driver='ODBC Driver 17 for SQL Server'
        self.server='DESKTOP-0TEJHE1'
        self.db='Pokemon'

class Database:
    def __init__(self, ConfigObject):
        self.engine = create_engine(f'mssql://@{ConfigObject.server}/{ConfigObject.db}?driver={ConfigObject.driver}')
        self.Connection = self.engine.connect()
        self.Session = 0

    def OpenSession(self):
        Maker = sessionmaker(bind=self.engine)
        self.Session = Maker()

    def CloseSession(self):
        self.Session.close()

#Database Classes
class pokemon(Base):
    __tablename__ = "pokemon"
    Id = Column('Id', Integer, primary_key=True)
    Name = Column('Name', String)
    Type1 = Column('Type1', String)
    Type2 = Column('Type2', String)
    HP = Column('HP', Integer)
    Atk = Column('Atk', Integer)
    Def = Column('Def', Integer)
    SpAtk = Column('SpAtk', Integer)
    SpDef = Column('SpDef', Integer)
    Speed = Column('Speed', Integer)
    Generation = Column('Generation', String)
    Legendary = Column('Legendary', Integer)

class combats(Base):
    __tablename__ = "combats"
    Id = Column(Integer, primary_key=True) #SQLAlchemy needs ID so we add column, wich dont exist in DB
    First_pokemon = Column(Integer, ForeignKey("pokemon.Id")) #Foreign key
    First_pokemon_rel = relationship("pokemon", foreign_keys = [First_pokemon]) #Related data, connected to this foreign key
    Second_pokemon = Column(Integer, ForeignKey("pokemon.Id"))
    Second_pokemon_rel = relationship("pokemon", foreign_keys = [Second_pokemon])
    BinaryWinner = Column('BinaryWinner', Integer)


Conf = ConnectionConfig()
Db = Database(Conf)

