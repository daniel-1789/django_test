from django.db import models


# Create your models here.
# https://docs.djangoproject.com/en/3.1/topics/db/models/
# After writing model definition, run "./manage.py makemigrations" and then "./manage.py migrate"
class FBATransaction(models.Model):
    """
    A single transaction from the FBA transaction report download
    """

    class Meta:
        db_table = "fba_transactions"

    date_time = models.DateTimeField(null=False, blank=False, db_column='date_time')

    # order types
    ADJUSTMENT = 'Adjustment'
    RETURN_FEE = 'FBA Customer Return Fee'
    INVENTORY_FEE = 'FBA Inventory Fee'
    ORDER = 'Order'
    ORDER_RETROCHARGE = 'Order_Retrocharge'
    REFUND = 'Refund'
    TRANSFER = 'Transfer'
    ORDER_TYPE_CHOICES = [
        (ADJUSTMENT, ADJUSTMENT),
        (RETURN_FEE, RETURN_FEE),
        (INVENTORY_FEE, INVENTORY_FEE),
        (ORDER, ORDER),
        (ORDER_RETROCHARGE, ORDER_RETROCHARGE),
        (REFUND, REFUND),
        (TRANSFER, TRANSFER),
    ]
    order_type = models.CharField(
        max_length=32,
        choices=ORDER_TYPE_CHOICES,
        blank=True,
        null=True,
        db_column='type'
    )

    order_id = models.CharField(max_length=32, blank=True, null=True)
    sku = models.CharField(max_length=32, blank=True, null=True)
    description = models.TextField(blank=True, null=True)  # never seen to be null
    quantity = models.IntegerField(null=True)
    order_city = models.CharField(max_length=64, blank=True, null=True)
    order_state = models.CharField(max_length=32, blank=True, null=True)
    order_postal = models.CharField(max_length=16, blank=True, null=True)
    total = models.DecimalField(null=False, decimal_places=2, max_digits=16)

