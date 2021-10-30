Perch Take-Home Test

First, make sure to install `django` https://docs.djangoproject.com/en/3.1/topics/install/#installing-official-release
Also install `rest_framework` https://www.django-rest-framework.org/#installation
Feel free to use any additional packages 

Three important files to look at in the `transactions` folder:
1. `models.py`
2. `example_transactions.csv`
3. `views.py`


In `models.py`, you will write the model definition for an `FBATransaction`

You will need to examine `example_transactions.csv` to determine what fields a transaction can have

After the model definition is completed, read the API endpoints stubbed out in `views.py` and add the functionality specified in the comments.

Postman is highly recommended to use to test your endpoints after writing them (https://www.postman.com/downloads/)
You can run the server by calling `python manage.py runserver` and route requests to `localhost:8000`.

