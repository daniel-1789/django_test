import datetime

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


def convert_string_to_datetime(date_string: str):
    """
    Given a date_string with a format like Nov 1, 2020 12:23:30 AM PDT, convert it to a datetime.
    This code takes advantage of the sample data only having PDT and PST, obviously in a production
    design that would not be sufficient

    params:
    date_string(str): The string to be converted into a datetime expected format Nov 1, 2020 12:23:30 AM PDT

    return: Python datetime object
    """
    date_string = date_string.replace(', ', ' ')
    date_string = date_string.replace(' PDT', ' -0900')
    date_string = date_string.replace(' PST', ' -0800')
    dt = datetime.datetime.strptime(date_string, '%b %d %Y %I:%M:%S %p %z')
    return dt


def do_filtering(query_dict: Dict):
    """
    Go through the query_dict and perform any of the queries that are specified in it.
    Take advantage of the lazy query characteristic of django and build the query iteratively

    params:
    query_dict(dict): Dictionary of filters apply

    return: Query result
    """

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
        parsed_start = convert_string_to_datetime(start_date)
        query = query.filter(date_time__gte=parsed_start)

    end_date = query_dict.get('end')
    if end_date:
        parsed_end = convert_string_to_datetime(end_date)
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

        NOTE - This POST caused me an inordinate amount of pain. I've never used Django before this'
        and I'm certain that there's something really obvious I missed to allow me to upload a CSV.
        However, whenever I tried to do so I ran into problems with text/csv - I kept running into
        problems with rendering the csv as opposed to a json. I experimented a little bit with
        using https://github.com/mjumbewu/django-rest-framework-csv but that didn't quite work though
        I think I was on the right track. However since this was described as intended to a relatively
        brief exercise I felt I'd well exceeded a reasonable amount of time searching for a solution.
        Were I in the office I'd probably be posting a slack along the lines of "what one line
        fix am I missing or where can I find this in stack overflow..."

        That said I did want to have some mechanism to take the data and insert it in the database
        so I went with the extremely brute-force method of changing this to accept a massive json blob
        that I converted from the sample csv file
        """

        # https://docs.djangoproject.com/en/3.1/ref/request-response/#django.http.HttpRequest.FILES

        for curr_row in request.data:
            curr_date = curr_row.get('date/time')
            if  curr_date:
                dt = convert_string_to_datetime(curr_date)
            else:
                continue

            entry_orm = FBATransaction(
                date_time=dt,
                order_type=curr_row.get('type'),
                order_id=curr_row.get('order id'),
                sku=curr_row.get('sku'),
                description=curr_row.get('description'),
                quantity=int(curr_row.get('quantity')) if curr_row.get('quantity') else None,
                order_city=curr_row.get('order city'),
                order_state=curr_row.get('order state'),
                order_postal=curr_row.get('order postal'),
                total=float(curr_row.get('total')) if curr_row.get('total') else None,
            )
            entry_orm.save()
        return Response("ok", status=status.HTTP_200_OK)


class TransactionsStatsView(GenericAPIView):
    """
    Returns aggregated stats of transactions by the given filters,

    Note - the specifications did not indicate what was to be done in the event of no matches, returning
    a dict of Nones in such a case
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
        if totals:
            stats = {
                'summed': sum(totals),
                'mean':  mean(totals),
                'median': median(totals),
            }
        else:
            stats = {
                'summed': None,
                'mean':  None,
                'median': None,
            }

        return Response(stats, status=status.HTTP_200_OK)
