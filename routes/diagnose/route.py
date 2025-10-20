
from flask import Blueprint
from routes.diagnose.controller import diagnose_plant

diagnose_bp = Blueprint('diagnose', __name__)

@diagnose_bp.route('/diagnose', methods=['POST'])
def diagnose():
    """Plant diagnosis endpoint - accepts image upload and returns diagnosis."""
    return diagnose_plant()

