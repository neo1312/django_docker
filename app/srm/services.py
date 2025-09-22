from .models import Supplier
from django.db.models import Max,Min

def calculate_scores():
    result=Supplier.objects.aggregate(
            max_credit=Max('credit_days'),
            min_credit=Min('credit_days'),
            max_delivery_cost=Max('delivery_cost'),
            min_delivery_cost=Min('delivery_cost'))

    maximum_credit=result["max_credit"] or 0
    minimum_credit=result["min_credit"] or 0
    delta_credit=maximum_credit-minimum_credit or 1

    maximum_delivery=result["max_delivery_cost"] or 0
    minimum_delivery=result["min_delivery_cost"] or 0
    delta_delivery=maximum_delivery-minimum_delivery or 1

    suppliers=Supplier.objects.all()

    for s in suppliers:
        credit_score = 1 + ((s.credit_days - minimum_credit)/ delta_credit)*4
        s.credit_score = round(credit_score,2)

        delivery_score= 5 - ((s.delivery_cost - minimum_delivery)/ delta_delivery)*4
        s.cost_delivery_score = round(delivery_score,2)

    Supplier.objects.bulk_update(suppliers, ['credit_score','cost_delivery_score'])
