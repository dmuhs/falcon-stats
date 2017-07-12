import logging

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Interval, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_or_create(session, model, **kwargs):
    # https://stackoverflow.com/a/6078058
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        logger.debug("%s instance found in the DB", model.__name__)
        return instance
    else:
        logger.debug("%s instance not found - creating it", model.__name__)
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


class UserAgent(Base):

    __tablename__ = "useragent"
    id = Column(Integer, primary_key=True, nullable=False)
    text = Column(String(512), nullable=False, unique=True)


class URI(Base):

    __tablename__ = "uri"
    id = Column(Integer, primary_key=True, nullable=False)
    text = Column(String(512), nullable=False, unique=True)


class Method(Base):

    __tablename__ = "method"
    id = Column(Integer, primary_key=True, nullable=False)
    text = Column(String(10), nullable=False, unique=True)


class IP(Base):

    __tablename__ = "ip"
    id = Column(Integer, primary_key=True, nullable=False)
    text = Column(String(16), nullable=False, unique=True)


class ContentType(Base):

    __tablename__ = "contenttype"
    id = Column(Integer, primary_key=True, nullable=False)
    text = Column(String(255), unique=True)


class Status(Base):

    __tablename__ = "httpstatus"
    id = Column(Integer, primary_key=True, nullable=False)
    text = Column(String(255), unique=True)


class ReqRespInfo(Base):

    __tablename__ = "stats"
    id = Column(Integer, primary_key=True, nullable=False)

    date = Column(DateTime, nullable=False)
    processed = Column(Interval, nullable=False)

    useragent_id = Column(Integer, ForeignKey(UserAgent.id), nullable=False)
    useragent = relationship("UserAgent")

    uri_id = Column(Integer, ForeignKey(URI.id), nullable=False)
    uri = relationship("URI")

    method_id = Column(Integer, ForeignKey(Method.id), nullable=False)
    method = relationship("Method")

    ip_id = Column(Integer, ForeignKey(IP.id), nullable=False)
    ip = relationship("IP")

    content_type_id = Column(
        Integer,
        ForeignKey(ContentType.id),
        nullable=False
    )
    content_type = relationship("ContentType")

    status_id = Column(Integer, ForeignKey(Status.id), nullable=False)
    status = relationship("Status")

    contentlength = Column(Integer)
