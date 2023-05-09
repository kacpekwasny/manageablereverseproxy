
from manageablereverseproxy.app import create_app, REPO_DIR
from manageablereverseproxy.db import db
from manageablereverseproxy.components.firewall_ip import app_add_firewall_ip_module
from manageablereverseproxy.components.authentication import app_add_authentication_module, require_auth
from manageablereverseproxy.components.reverseproxy import app_add_reverseproxy_module


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{str(REPO_DIR / 'assets/test.db')}"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

        app_add_firewall_ip_module(app)
        app_add_authentication_module(app)
        app_add_reverseproxy_module(app, "http://127.0.0.1:8001/")
        db.drop_all()
        db.create_all()
        db.session.commit()


