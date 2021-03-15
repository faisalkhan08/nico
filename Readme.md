The first thing to do is to clone the repository:

$ git clone https://github.com/faisalkhan08/nico.git

Setup project environment with virtualenv and pip.


$ virtualenv project-env
$ source project-env/bin/activate
$ cd nico
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py runserver

