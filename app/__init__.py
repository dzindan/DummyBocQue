import os

from flask import Flask

from .paths import get_bundle_dir
from .version import APP_VERSION


def create_app() -> Flask:
    bundle_dir = get_bundle_dir()
    app = Flask(
        __name__,
        template_folder=os.path.join(bundle_dir, "app", "templates"),
        static_folder=os.path.join(bundle_dir, "app", "static"),
    )
    app.secret_key = os.urandom(24)

    from .routes.home import bp as home_bp
    from .routes.hexagram import bp as hexagram_bp
    from .routes.divination import bp as divination_bp
    from .routes.notes import bp as notes_bp
    from .routes.study import bp as study_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(hexagram_bp)
    app.register_blueprint(divination_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(study_bp)

    @app.context_processor
    def inject_app_version():
        return {"app_version": APP_VERSION}

    return app
