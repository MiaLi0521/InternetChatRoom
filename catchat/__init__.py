import os

import click
from flask import Flask

from catchat.model import User, Message
from catchat.settings import config
from catchat.extensions import db, login_manager, csrf, socketio, moment
from catchat.blueprints.auth import auth_bp
from catchat.blueprints.chat import chat_bp
from catchat.blueprints.oauth import oauth_bp
from catchat.blueprints.admin import admin_bp


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask('catchat')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)

    return app


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app)
    moment.init_app(app)


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(admin_bp)


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help="Create after drop.")
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--message', default=300, help="Quantity of messages, default is 300.")
    def forge(message):
        """Generate fake data."""
        import random
        from sqlalchemy.exc import IntegrityError

        from faker import Faker

        fake = Faker()

        click.echo('Initializing the database...')
        db.drop_all()
        db.create_all()

        click.echo('Forging the data')
        admin = User(nickname="admin", email="admin@helloflask.com")
        admin.password = "admin123"
        db.session.add(admin)
        db.session.commit()

        click.echo('Generating users...')
        for i in range(50):
            user = User(nickname=fake.name(), bio=fake.sentence(), github=fake.url(), website=fake.url(),
                        email=fake.email())
            user.password = user.email
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

        click.echo('Generating messages...')
        for i in range(message):
            message = Message(
                author=User.query.get(random.randint(1, User.query.count())),
                body=fake.sentence(),
                timestamp=fake.date_time_between('-30d', '-2d'),
            )
            db.session.add(message)
        db.session.commit()
        click.echo('Done.')
