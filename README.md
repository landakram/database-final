Athletics Organizer
===================

Mark and Sam's awesome Database Systems final project.

Installation
------------

We assume that `mysql` and `python` are already installed.

1. Get `pip`:
    
        $ easy_install pip

2. Get `virtualenv`:

        $ pip install virtualenv

3. Get `virtualenvwrapper`. It makes using `virtualenv` easier:

        $ pip install virtualenvwrapper

4. Add this to your `.bashrc` or run in your terminal:

        source /usr/local/bin/virtualenvwrapper.sh

5. In the terminal, make a `virtualenv` for this project:

        $ mkvirtualenv database-final

6. You should automatically be working in the environment. In your shell,
you should see something like:

        (database-final) $ 

7. To install the required dependencies for this project in one fell swoop,
`cd` to the project root and then run:

        (database-final) $ pip install -r requirements.txt

8. Now run the server:

        (database-final) $ python app.py
        * Running on http://127.0.0.1:5000/

The server should now be running on port 5000.

    

    
