import logging

import falcon
from falcon import testing

from falconstats import FalconStatsMiddleware, models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.DEBUG)
# Illegal methods are PUT, HEAD, PATCH, DELETE
test_resource = testing.SimpleTestResource(
    status="418 I'm a teapot",
    json={"message": "test"}
)


class TestStatsMiddleware(testing.TestCase):

    def setUp(self):
        super(TestStatsMiddleware, self).setUp()
        fsm = FalconStatsMiddleware(
            debug=True,
            session=self.Session,
            engine=self.engine
        )
        self.app = falcon.API(middleware=[fsm])
        self.app.add_route("/stats", test_resource)

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:")
        # make sure object relations don't expire after setup session is closed
        cls.Session = sessionmaker(bind=cls.engine, expire_on_commit=False)

    def get_latest_rri(self, session):
        return session.query(models.ReqRespInfo)\
            .order_by(models.ReqRespInfo.id.desc()).first()

    def check_rri(self, rri, method, status, endpoint="/stats"):
        self.assertEqual(rri.status.text, status)
        self.assertEqual(rri.ip.text, "127.0.0.1")
        self.assertEqual(rri.method.text, method)
        self.assertIsNotNone(rri.date)
        self.assertIsNotNone(rri.processed)
        self.assertEqual(
            rri.useragent.text,
            "curl/7.24.0 (x86_64-apple-darwin12.0)"
        )
        self.assertEqual(rri.uri.text, "http://falconframework.org" + endpoint)

    def assertContentIsNone(self, rri):
        self.assertIsNone(rri.contentlength)
        self.assertIsNone(rri.content_type.text)

    def test_http_get(self):
        self.simulate_get("/stats")
        session = self.Session()
        rri = self.get_latest_rri(session)
        self.check_rri(rri, "GET", "418 I'm a teapot")
        self.assertIsNone(rri.contentlength)
        self.assertIsNone(rri.content_type.text)
        session.close()

    def test_http_post(self):
        self.simulate_post(
            path="/stats",
            body="This is a test.",
            headers={"Content-Type": "text/plain"}
        )
        session = self.Session()
        rri = self.get_latest_rri(session)
        self.check_rri(rri, "POST", "418 I'm a teapot")
        self.assertEqual(rri.contentlength, 15)
        self.assertEqual(rri.content_type.text, "text/plain")
        session.close()

    def test_http_put(self):
        self.simulate_put("/stats")
        session = self.Session()
        rri = self.get_latest_rri(session)
        self.check_rri(rri, "PUT", "405 Method Not Allowed")
        self.assertContentIsNone(rri)
        session.close()

    def test_http_head(self):
        self.simulate_head("/stats")
        session = self.Session()
        rri = self.get_latest_rri(session)
        self.check_rri(rri, "HEAD", "405 Method Not Allowed")
        self.assertContentIsNone(rri)
        session.close()

    def test_http_options(self):
        self.simulate_options("/stats")
        session = self.Session()
        rri = self.get_latest_rri(session)
        self.check_rri(rri, "OPTIONS", "200 OK")
        self.assertContentIsNone(rri)
        session.close()

    def test_http_patch(self):
        self.simulate_patch("/stats")
        session = self.Session()
        rri = self.get_latest_rri(session)
        self.check_rri(rri, "PATCH", "405 Method Not Allowed")
        self.assertContentIsNone(rri)
        session.close()

    def test_http_delete(self):
        self.simulate_delete("/stats")
        session = self.Session()
        rri = self.get_latest_rri(session)
        self.check_rri(rri, "DELETE", "405 Method Not Allowed")
        self.assertContentIsNone(rri)
        session.close()

    def test_invalid_route(self):
        self.simulate_get("/invalid")
        session = self.Session()
        rri = self.get_latest_rri(session)
        self.check_rri(rri, "GET", "404 Not Found", endpoint="/invalid")
        self.assertContentIsNone(rri)
        session.close()
