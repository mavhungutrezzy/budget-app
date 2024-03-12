# Finance by Month
<img src="https://djfdm802jwooz.cloudfront.net/static/project_images/0e3455cc05a340fea87230575ced49f5.png" width="400" height="400" />
This is an extremely lean monthly budgeting program.  It allows you to add monthly income/expense transactions and perform simple economic forecasts into the future, one month's budget at a time.
<br><br>
This app is basically just Django, JavaScript, and CSS (SASS)

# Running the app
- **Pull the repo and run the Django development server**
  - This is the easiest way to get started.
  - Create a virtual environment `virtualenv venv` and activate it with `source venv/bin/activate`
  - Inside the virtual environment, run `pip install -r requirements.txt`
  - Then make migrations with `python manage.py makemigrations`
  - Then migrate with `python manage.py migrate`
  - Then run the server with `python manage.py runserver`
  - Then go to http://localhost:8000
