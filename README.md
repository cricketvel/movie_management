# movie_management

Steps to Setup the Project


Install python3

sudo apt-get install virtualenv

virutalenv -p python {env_name}

pip install -r requirements.txt

git clone {repo_link}

Navigate into the project folder where manage.py exists

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
