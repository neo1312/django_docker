# srm/handlers.py

from ..services import calculate_scores

def recalculate_supplier_score(sender, instance, **kwargs):
    calculate_scores()
