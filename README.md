# Project 1

Web Programming with Python and JavaScript

1. In a terminal window, navigate into your project1 directory.
2. Run ( pip3 install -r requirements.txt ) in your terminal window to make sure that all of the necessary Python packages (Flask and SQLAlchemy, for instance) are installed.
3. Set the environment variable FLASK_APP to be application.py. On a Mac or on Linux, the command to do this is ( export FLASK_APP=application.py )
4. You may optionally want to set the environment variable FLASK_DEBUG to 1, ( FLASK_DEBUG=1 ) which will activate Flask’s debugger and will automatically reload your web application whenever you save a change to a file.
5. Set the environment variable DATABASE_URL to be the URI of your database, ( export DATABASE_URL="postgres://fwlxeswjgofjbi:6c944785dffa9a2c64e1af929269e1419342c959d3031297b7d722f05ade2021@ec2-52-207-25-133.compute-1.amazonaws.com:5432/db38d7e607qhgm
" ) .which you should be able to see from the credentials page on Heroku.
6. Run ( flask run ) to start up your Flask application.
