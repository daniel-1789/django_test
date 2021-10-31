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


# Solution Notes
## Implementation
This was my first experience with Django so I'm certain the solution is a little on the ungraceful side
in parts. However, I overall did find I enjoyed working with it.

There's a few places where I wound up diverging from the spec.

First, a column called "date/time" proved a bit tricky. Obviously that's
not a valid Python name though there are mechanisms to allow columns
to have different names than their django equivalent. That's the approach
I took in my initial migration but the results of querying that were 
consistently None/null. Given all the discussions I can find online
concur that having a slash within a column name is a "bad idea" - something
you might be able to pull off with some escape characters but probably
dangerous. I therefore replaced the slash with an underscore.

Second, when performing aggregations I didn't see any guidance on what
to return if the filters resulted in nothing being returned. I decided
to return a dictionary of Nones but it would be just as easy (easier
actually) to return nothing.

The most serious issue I ran into is trying to use a POST to upload
a csv file to django proved very problematic. The POST was called
just fine the problem was I coundn't get a renderer that would work
with text/csv. This is the sort of thing where never having used django
previously definitely was problematic. I experimented with using https://github.com/mjumbewu/django-rest-framework-csv
and I think I was on the right track with that but it began becoming extremely time-consuming. As this was
described as something should only bne a few hours at most it seemed
more appropriate to move onto the other parts of the problem. I therefore
made the POST function in an extremely brute-force manner - I converted the
sample csv file into a json and simply passed that json in the POST. That's definitely 
not a solution I'd take into production - were we all working together this is
an occasion where I'd fire off a slack to the team asking "what simple thing
am I missing" and after all was said and done learned something interesting.


## Possible Optimizations
I definitely took advantage of the data set I was presented with - my code is
a long ways from handling corner cases. 

I didn't see an obvious candidate for a primary key - obviously order_id seemed a reasonable
starting point but there were a number of cases where it was null. As an enhancement I'd
probably simply automatically generate a unique id when creating the ORMs.

Finally, I left the data as-is but there's clearly a lot of opportunity for data-cleaning.


## Tools Used
In additition to the django suite I wound up doing a lot of experimentation with postman and used DBBrowser for SQLite.

