from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from decimal import Decimal
from flask_socketio import SocketIO

db = SQLAlchemy()
mail = Mail()
socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    socketio.init_app(app, cors_allowed_origins='*', is_async=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:root@110.42.178.4:5555/turn4"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["SECRET_KEY"] = "BaiguiSB"
    app.config["EXPIRATION"] = 3600
    app.config["FILE_PATH"] = app.config.root_path[:-14] + "static\\"

    app.config['MAIL_SERVER'] = 'smtp.qq.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = "1219967460@qq.com"
    app.config['MAIL_PASSWORD'] = "zcdazfcyywxyhaaj"
    mail.init_app(app)

    app.config["PROFIT_FACTOR"] = Decimal("0.01")
    db.init_app(app)

    from ..user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/api/v1/user')

    from ..market import market as market_blueprint
    app.register_blueprint(market_blueprint, url_prefix="/api/v1/market")

    from ..order import order as order_blueprint
    app.register_blueprint(order_blueprint, url_prefix="/api/v1/order")
    return app, socketio
