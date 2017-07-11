import logging
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import (IP, URI, Base, ContentType, Method, ReqRespInfo, Status,
                     UserAgent, get_or_create)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


REQ_RESP_FORMAT = """
Date: {date}
Processing Time: {processed:.4f}ms
Method: {method}
Scheme: {scheme}
URI: {uri}
IP: {ip}
User-Agent: {useragent}
Content-Type: {contenttype}
Content-Length: {contentlength}
Status: {status}
Success: {success}
"""


class FalconStatsMiddleware(object):

    def __init__(self, debug=False, **kwargs):
        if not debug:
            DB = "mysql+pymysql://{}:{}@{}/{}".format(
                kwargs["db_user"],
                kwargs["db_pass"],
                kwargs["db_addr"],
                kwargs["db_name"]
            )
            engine = create_engine(DB, pool_pre_ping=True)
            self.Session = sessionmaker(bind=engine)
        else:
            engine = kwargs["engine"]
            self.Session = kwargs["session"]
        Base.metadata.create_all(bind=engine)

    def process_request(self, req, resp):
        # start processing start time
        req.context["start_time"] = datetime.now()

    def process_response(self, req, resp, resource, req_succeeded):
        """Post-processing of the response (after routing)."""
        now = datetime.now()
        delta = now - req.context["start_time"]

        session = self.Session()
        uag = get_or_create(session, UserAgent, text=req.user_agent)
        uri = get_or_create(session, URI, text=req.uri)
        mtd = get_or_create(session, Method, text=req.method)
        ipa = get_or_create(session, IP, text=req.remote_addr)
        ctt = get_or_create(session, ContentType, text=req.content_type)
        stt = get_or_create(session, Status, text=resp.status)

        rri = ReqRespInfo(
            date=now,
            processed=delta,
            useragent_id=uag.id,
            uri_id=uri.id,
            method_id=mtd.id,
            ip_id=ipa.id,
            content_type_id=ctt.id,
            status_id=stt.id,
            contentlength=req.content_length
        )
        session.add(rri)
        session.commit()
        session.close()

        logger.debug(REQ_RESP_FORMAT.format(
            date=now.strftime("%c"),
            processed=delta.total_seconds() * 1000,  # milliseconds
            method=req.method,
            scheme=req.scheme,
            uri=req.uri,
            ip=req.remote_addr,
            useragent=req.user_agent,
            contenttype=req.content_type,
            contentlength=req.content_length,
            status=resp.status,
            success=req_succeeded
        ))
