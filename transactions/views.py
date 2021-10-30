from django.http import HttpRequest
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from typing import Dict
from statistics import mean,median

# *** This will be highly relevant ***
# https://docs.djangoproject.com/en/3.1/topics/db/queries/
from transactions.models import FBATransaction


def do_filtering(query_dict: Dict):

    query = FBATransaction.objects.all()

    order_type = query_dict.get('type')
    if order_type:
        query = query.filter(order_type=order_type)

    city = query_dict.get('city')
    if city:
        query = query.filter(order_city=city)

    state = query_dict.get('state')
    if state:
        query = query.filter(order_state=state)

    postal = query_dict.get('postal')
    if postal:
        query = query.filter(order_postal=postal)

    skus = query_dict.get('skus')
    if skus:
        split_skus = skus.split(',')
        query = query.filter(sku__in=split_skus)

    start_date = query_dict.get('start')
    if start_date:
        parsed_start = parse_date(start_date)
        query = query.filter(date_time__gte=parsed_start)

    end_date = query_dict.get('end')
    if end_date:
        parsed_end = parse_date(end_date)
        query = query.filter(date_time__lte=parsed_end)

    return query.values()


class TransactionsListView(GenericAPIView):
    """
    Handles retrieving and creating transactions
    """

    permission_classes = (AllowAny,)

    def get(self, request: HttpRequest):
        """
        Returns a list of transactions by the given filters

        params:
        type (str): Returns transactions of this type
        skus (list): Returns transactions with this SKU, should be sent/parsed as a comma separated string if multiple SKU's
        start (str): Returns transactions occurring after this date/time
        end (str): Returns transactions occurring before this date/time
        city (str): Returns transactions in this city
        state (str): Returns transactions in this state
        postal (str): Returns transactions in this postal address
        """
        # Dictionary containing all parameters sent in the query string
        request_data = request.GET
        query_result = do_filtering(query_dict=request_data)

        return Response(query_result, status=status.HTTP_200_OK)


    @csrf_exempt
    def post(self, request: HttpRequest):
        """
        Imports a CSV file of transactions
        """

        # https://docs.djangoproject.com/en/3.1/ref/request-response/#django.http.HttpRequest.FILES
        for _, file in request.FILES.items():
            pass

        return Response("ok", status=status.HTTP_200_OK)


class TransactionsStatsView(GenericAPIView):
    """
    Returns aggregated stats of transactions by the given filters
    """

    permission_classes = (AllowAny,)

    def get(self, request: HttpRequest):
        """
        Returns a response containing the summed, average, and median totals for transactions using any given filters.

        params:
        type (str): Returns transactions of this type
        skus (list): Returns transactions with this SKU, should be sent/parsed as a comma separated string if multiple SKU's
        start (str): Returns transactions occurring after this date/time
        end (str): Returns transactions occurring before this date/time
        city (str): Returns transactions in this city
        state (str): Returns transactions in this state
        postal (str): Returns transactions in this postal address
        """
        # Contains all parameters sent in the query string
        request_data = request.GET
        query_result = do_filtering(query_dict=request_data)
        for curr_entry in query_result:
            print(curr_entry)
        totals = [curr_entry.get('total') for curr_entry in query_result]
        stats = {
            'summed': sum(totals),
            'mean':  mean(totals),
            'median': median(totals),
        }
        return Response(stats, status=status.HTTP_200_OK)
