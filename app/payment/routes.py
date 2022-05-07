from flask_login import login_required

from . import payment_bp


@payment_bp.route("/get_premium/")
@login_required
def get_premium():
    # TODO: make diese, but am besten nicht stripe, sondern mit diese andere
    return "TODO"
