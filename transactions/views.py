from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


# *** This will be highly relevant ***
# https://docs.djangoproject.com/en/3.1/topics/db/queries/
from transactions.models import FBATransaction


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
        query = FBATransaction.objects.all()

        order_type = request_data.get('type')
        if order_type:
            query = FBATransaction.objects.filter(order_type=order_type)

        city = request_data.get('city')
        if city:
            query = FBATransaction.objects.filter(order_city=city)

        state = request_data.get('state')
        if state:
            query = FBATransaction.objects.filter(order_state=state)


        foo = query.values()
        return Response(foo, status=status.HTTP_200_OK)

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

        return Response("ok", status=status.HTTP_200_OK)
