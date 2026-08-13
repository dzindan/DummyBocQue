import os
from datetime import datetime

from flask import Flask
from flask_wtf import CSRFProtect

from .kinhdich import vn_time
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
    # Every POST route here mutates state (delete history/notes, add notes)
    # with no auth in front of it - without CSRF protection, a form on any
    # other site could silently submit to these endpoints in a logged-in
    # user's browser. CSRFProtect checks a token on every POST/PUT/PATCH/
    # DELETE automatically; the 6 <form method="post"> templates each carry
    # a hidden csrf_token field for it to check.
    CSRFProtect(app)

    @app.template_filter("vn_datetime")
    def vn_datetime(iso_utc_str, fmt="%Y-%m-%d %H:%M"):
        """Formats a stored UTC ISO timestamp (created_at) as Vietnam
        local time for display - storage stays UTC/unambiguous, only the
        rendering converts, so this is the one place that needs to
        change if that ever needs to differ per-user."""
        dt = datetime.fromisoformat(iso_utc_str)
        return vn_time.to_vn(dt).strftime(fmt)

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
