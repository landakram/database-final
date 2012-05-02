Athletics Organizer
===================

Mark and Sam's awesome Database Systems final project.

Installation
------------

We assume that `mysql` and `>= python 2.6` are already installed on a OS X
system. We tested our setup with both Lion and Snow Leopard.

1. Get `pip`:
    
        $ sudo easy_install pip

2. Get `virtualenv`:

        $ sudo pip install virtualenv

3. Get `virtualenvwrapper`. It makes using `virtualenv` easier:

        $ sudo pip install virtualenvwrapper

4. Add this to your `.bashrc` or run in your terminal:

        source /usr/local/bin/virtualenvwrapper.sh

5. In the terminal, make a `virtualenv` for this project:

        $ mkvirtualenv database-final

6. You should automatically be working in the environment. In your shell,
you should see something like:

        (database-final) $ 

If you don't, then you can enter a virtual environment by running:

        $ workon database-final

`database-final` is just the name of the virtualenv you created.

7. To install the required dependencies for this project in one fell swoop,
`cd` to the project root and then run:

        (database-final) $ pip install -r requirements.txt

8. Now, let's populate our database. In the `data` folder, there 
is a file called `all.sql`, which containts both the schema and 
all generated data we used. In the project root:

        (database-final) $ cd data
        (database-final) $ mysql
        mysql> source all.sql

9. Now run the server:

        (database-final) $ python app.py
        * Running on http://127.0.0.1:5000/

The server should now be running on port 5000.

    
Overview of Included Files
--------------------------

In the project root, we have a `README` with instructions for setting up the server. 
The actual server code is contained in `app.py`. Settings for the server, including
the database name, host, username, and password are in `settings.py`. 

We also have several folders. `static` and `templates` are part of the server.
`static` contains static resources like images, javascript code, and css. For our
server, we used a UI framework called [Twitter Bootstrap](http://twitter.github.com/bootstrap/). 
The `templates` folder contains various html templates used by our server. Flask
templates are similar to JSPs, except that most of the application logic is done in `app.py`.
Variables can be passed to templates and templates have limited control flow features like
`for` loops and `if` statements. 

The `data` folder contains various scripts and text files we used for generating
our data. We have concatenated the result of running all the scripts into `all.sql`,
but they are available for your perusal. The `docs` folder contains our final
write-up, progress reports, and other documentation, like our ER diagram. 

    
