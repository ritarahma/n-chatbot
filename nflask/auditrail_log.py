from flask import Blueprint
from nflask.signals import audittrail_signals

auditraillog = Blueprint("audit_trail", __name__)

def auditrail_signals(konten_tipe, konten_id, isi, user_id, actions):
    """Auditrail logs Signal."""
    audittrail_signals.send(
        auditraillog,
        konten_tipe=konten_tipe,
        konten_id=konten_id,
        isi=isi,
        user_id=user_id,
        actions=actions)
