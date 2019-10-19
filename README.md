---ITEM CATALOG PROJECT---

OVERVIEW:
This application that provides a list of items within a variety of categories as well as provide a user registration and authentication system using Google Sign-In. Registered users will have the ability to post, edit and delete their own items.

USAGE:
The below instructions assume you have installed the Vagarant Virtual Machine as required for the Udacity Full Stack Nanodegree.

1. Copy the submitted files and folders to the shared folder you have set up on the Vagrant Virtual Machine. Namely, these are:
	- application.py
	- client_secrets.json
	- database_setup.py
	- createCaetgoriesAndItems.py
	- itemCategory.db
	- README.md
	- templates folder and all contents
	- static folder and all contents

2. In order to run this web application you may have to run the following commands on the virtual machine, if you haven't done so already:

	sudo pip3 install sqlalchemy
	sudo pip3 install flask
	sudo pip3 install oauth2client
	sudo pip3 install flask_httpauth

3. If you want to recreate the itemCategory.db file from scratch you can delete it and execute the following files on the virtual machine from the shared folder location.

	python3 database_setup.py
	python3 createCategoriesAndItems.py

4. To run the web application execute the application.py file from the shared folder with the following command:
	
	python3 application.py

5. The web application should now be running on you Vagrant Virtual Machine.

6. You can access the web application with the followig link from the browser on your host machine.

	http://localhost:8000

7. To create, edit or delete items you will need to login using the login button in the top right.

8. You can access the json end points as follows:

	All categories and items:
	http://localhost:8000/catalog.json
	
	A specific category (e.g. Snowboarding) and items:
	http://localhost:8000/catalog/Snowboarding.json

	A specific item (e.g. Skis) in a category (e.g. Snowboarding):
	http://localhost:8000/catalog/Snowboarding/Skis.json
	

