import sqlalchemy
import yaml

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, backref, relationship

Base = declarative_base()

def init():
    Base.metadata.create_all(get_engine())

def get_engine():
    connection_string = get_config().get_global_parameter('sql')
    engine = sqlalchemy.create_engine(connection_string)
    return engine

def get_config():
    conf = Config('conf.yaml')
    return conf

class Tribune(Base):
    __tablename__ = 'tribune'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=42), unique=True)
    timezone = Column(String(length=42))

class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)

    post_id = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)
    info = Column(String(length=256), nullable=False)
    login = Column(String(length=256), nullable=True)
    message = Column(Text, nullable=False)

    tribune_id = Column(Integer, ForeignKey('tribune.id'))
    tribune = relationship('Tribune')

    __table_args__ = (UniqueConstraint('post_id', 'date', 'tribune_id'),)

    def __str__(self):
        ret = self.date.strftime('[%H:%M:%S] ')
        ret += self.login if self.login else self.info
        ret += ' '
        ret += self.message
        return ret

class Config:
    default_conf = 'default'

    def __init__(self, conf_file):
        with open(conf_file) as yamlconf:
            self.conf = yaml.load(yamlconf)

    def get_boards(self):
        for boardname in self.conf:
            if boardname != 'default':
                yield boardname

    def get_parameter(self, board, param_name):
        value = None
        try:
           value = self.conf[board][param_name]
        except KeyError:
            try:
                value = self.conf[Config.default_conf][param_name]
            except KeyError:
                logging.warn('No parameter <%s> in configuration' % param_name)
        return value

    def get_global_parameter(self, param_name):
        value = None
        try:
            value = self.conf['default'][param_name]
        except KeyError:
            logging.warn('No parameter <%s> in configuration' % param_name)
        return value
