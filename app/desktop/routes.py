from app.desktop import bp
from flask import render_template
from flask_login import current_user, login_required
from app.decorators import active_required
from app.utils import check_notitications


@bp.route("/")
@login_required
@active_required
def desktop():
    """
    Renders the desktop page.

    Returns:
        The rendered desktop page as a response.
    """
    return render_template(
        "desktop/index.html",
        is_authenticated=True,
        is_admin=current_user.is_admin(),
        has_notifications=check_notitications(),
        title="Bureau",
    )
