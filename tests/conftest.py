from types import SimpleNamespace

import flask
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker, relationship
import sqlalchemy as sqa


@pytest.fixture
def app(request):
    app = flask.Flask(request.module.__name__)
    app.testing = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    return app


@pytest.fixture
def request_context(app):
    return app.test_request_context


@pytest.fixture
def engine():
    return create_engine('sqlite:////tmp/test.db')


@pytest.fixture
def db_session(engine):
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    return db_session


@pytest.fixture
def base_model(app, engine, db_session):
    model = declarative_base()
    model.query = db_session.query_property()
    return model


@pytest.fixture
def models(base_model, engine):
    class User(base_model):
        __tablename__ = "users"
        id = sqa.Column("id", sqa.Integer, primary_key=True)
        first_name = sqa.Column(sqa.String(50))
        last_name = sqa.Column(sqa.String(50))
        username = sqa.Column(sqa.String(50), unique=True)
        birth_date = sqa.Column(sqa.DateTime)
        address_id = sqa.Column(sqa.Integer, sqa.ForeignKey("addresses.id"), nullable=True)

        address = relationship("Address", back_populates="user")

    class Address(base_model):
        __tablename__ = "addresses"
        id = sqa.Column("id", sqa.Integer, primary_key=True)
        road = sqa.Column(sqa.String(50))

        user = relationship("User", back_populates="address")

    base_model.metadata.create_all(bind=engine)

    yield SimpleNamespace(
        User=User,
        Address=Address
    )
    base_model.metadata.drop_all(bind=engine)
