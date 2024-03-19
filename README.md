The application is implemented using Django as it is the framework I am most familiar with, though a ligher weight fraemwork may have made a little more sense, as Django is quite heavily tied to the ORM and the requirements were not to use the ORM.

It uses Django ninja for creating the API, as it is a nice library on to of Django, lighter weight than DRF and provides data valiadation. Though not using the ORM meant that I needed to write a lot of my own code. 

I created a few management command to create the tables and load the fixture data.


To start everything use 
    `docker compose up -- build`. 

You may need to stop and restart the docker compose containers as the web server starts before the database is ready on my development machine.

Check the name of your docker containers with 
    `docker ps`

There should be one with web-1 in the name , like origenai-web-1

To setup the database use the follwing command (you may need to change the container name to what you saw in the previous command)
`docker exec -it origenai-web-1 python manage.py setup_database`



In order to load the fixtures use teh following command. (You may need to use `docker ps` to get the name of the correct web server container)

`docker exec -it origenai-web-1 python manage.py load_fixtures`

in order to run the tests use 

`docker exec -it origenai-web-1 python manage.py test`
