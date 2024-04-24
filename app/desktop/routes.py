from app.desktop import bp
from flask_login import login_required
from flask import render_template

@bp.route('/3d', methods=['GET'])
@login_required
def three_d_desktop():
    return render_template('desktop/3d_index.html')