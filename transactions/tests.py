from django.test import TestCase, Client

# Create your tests here.
from transactions.models import FBATransaction
from transactions.views import convert_string_to_datetime, TransactionsListView


class Transactions(TestCase):
    def setUp(self):
        lightsaber_orm = FBATransaction(
            date_time=convert_string_to_datetime('Nov 1, 2020 12:23:30 AM PDT'),
            order_type='Order',
            order_id='66',
            sku='bled-kyber',
            description='Lightsaber of former Jedi Anakin Skywalker',
            quantity=1,
            order_city='Mos Espa',
            order_state=None,
            order_postal='Executor',
            total=455.65,
        )
        lightsaber_orm.save()

        tie_figher_orm = FBATransaction(
            date_time=convert_string_to_datetime('Dec 1, 2020 12:23:30 AM PDT'),
            order_type='Refund',
            order_id='67',
            sku='tie-bomber',
            description='TIE Fighter',
            quantity=1,
            order_city='Coruscant',
            order_state='Core',
            order_postal=None,
            total=789.01,
        )
        tie_figher_orm.save()

    def test_basic_query(self):
        lightsaber_orm = FBATransaction.objects.get(sku='bled-kyber')
        assert lightsaber_orm.order_id == '66'

    def add_x_wing(self):
        x_wing_orm = FBATransaction(
            date_time=convert_string_to_datetime('Dec 2, 2020 12:23:30 AM PDT'),
            order_type='Order',
            order_id='68',
            sku='x-wing',
            description='X-Wing Fighter',
            quantity=1,
            order_city='Yavin',
            order_state='Outer Rim',
            order_postal=None,
            total=999.01,
        )
        x_wing_orm.save()

    def test_get(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')

        resp = c.get('/api/transactions/?start=Nov 1, 2020 12:23:30 AM PDT&end=Nov 25, 2020 12:23:30 AM PDT')
        data = resp.data
        for row in data:
            assert row.get('sku') == 'bled-kyber'

        resp = c.get('/api/transactions/?start=Nov 1, 2020 12:23:30 AM PDT&end=Nov 25, 2021 12:23:30 AM PDT')
        data = resp.data
        for row in data:
            assert row.get('sku') in {'bled-kyber', 'tie-bomber'}

        resp = c.get('/api/transactions/?start=May 10, 2002 12:23:30 AM PDT&end=May 21, 2005 12:23:30 AM PDT')
        data = resp.data
        assert not data

        resp = c.get('/api/transactions/?start=Nov 1, 2020 12:23:30 AM PDT&skus=bled-kyber')
        data = resp.data
        for row in data:
            assert row.get('order_city') == 'Mos Espa'

        resp = c.get('/api/transactions/?start=Nov 1, 2020 12:23:30 AM PDT&state=Core&skus=bled-kyber')
        data = resp.data
        assert not data

        resp = c.get('/api/transactions/?start=Nov 1, 2020 12:23:30 AM PDT&skus=bled-kyber,tie-bomber')
        data = resp.data
        for row in data:
            assert row.get('sku') in {'bled-kyber', 'tie-bomber'}

        resp = c.get('/api/transactions/?postal=Executor')
        data = resp.data
        for row in data:
            assert row.get('sku') in {'bled-kyber'}

        resp = c.get('/api/transactions/?state=Core')
        data = resp.data
        for row in data:
            assert row.get('sku') in {'tie-bomber'}


    def test_get_stats(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')

        resp = c.get('/api/transactions/stats/?start=Nov 1, 2020 12:23:30 AM PDT&end=Nov 25, 2020 12:23:30 AM PDT')
        data = resp.data
        assert data.get('summed') == data.get('mean') == data.get('median') # only one entry

        resp = c.get('/api/transactions/stats/?start=May 10, 2002 12:23:30 AM PDT&end=May 21, 2005 12:23:30 AM PDT')
        data = resp.data
        assert not data.get('summed') and not data.get('mean') and not data.get('median')

        resp = c.get('/api/transactions/stats/?start=Nov 1, 2020 12:23:30 AM PDT&skus=bled-kyber,tie-bomber,x-wing')
        data = resp.data
        assert data.get('summed') != data.get('mean')
        assert data.get('mean') == data.get('median')
        assert data.get('summed') != data.get('median')

        self.add_x_wing()
        resp = c.get('/api/transactions/stats/?start=Nov 1, 2020 12:23:30 AM PDT&skus=bled-kyber,tie-bomber,x-wing')
        data = resp.data
        assert data.get('summed') != data.get('mean')
        assert data.get('mean') != data.get('median')
        assert data.get('summed') != data.get('median')

