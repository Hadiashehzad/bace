Additional Documentation for New Features

This new documentation describes a series of new features available in this update that should make it easier to work with multiple databases or host your application on other platforms.

The document details a few pages that could be added to the BACE documentation site.
Before they are added and before merging this branch into main, I recommend someone else work through these instructions and ensure they work and are easily followed.

This document contains three "pages":

- "Configure Database (Optional)" describes how to set up your app to work with a MongoDB database and instructs users on what files should be changed in order to connnect the app with other database formats.
- "Creating a MongoDB  Atlas Database" describes how to set up a MongoDB Atlas database and lists what information should be stored to connect with your database in the app.
- "Deployment Options" describes the main ways the app can be deployed in it's current format.
It will also instruct users on what files need to be changed in order to deploy the application elsewhere and provide resources for further research.
- "Flask/MongoDB Deployment" describes the process of deploying the application as a typical Flask app on PythonAnywhere that is connected to a MongoDB database.
It's infeasible/out of scope to walk through all different deployment options, but this example should provide users with a helpful example of what it looks like to deploy BACE outside of the AWS ecosystem.

# Configure Database (Optional)

This section provides users with details on how to configure your application to connect with different databases.
When you follow the steps to deploy your application on AWS, your application template builds a DynamoDB database that is connected to your application.
If you plan to deploy your BACE application using that method, you can skip this section.
However, if you would like to connect your app to an alternative database type, follow these steps to do so.

The database configuration for you application is setup by the `app/database/db.py` script.

The script configures the database connection and defines three key functions:

 - `get_db_table()`: forms a connection to your database
 - `find_item()`: queries your database for an item by key
 - `create_item()`: creates/puts a new item into your table
 - `update_{db}_item()`: defines how to update an item in a given database type. Current configurations describe updates for DynamoDB and MongoDB connections
 - `update_item()`: calls `update_{db}_item()` in your application script for your specified database type.
 - `table`: defines the connection to the database that is used in `app/app.py`

Note on using alternative databases to DynamoDB:
If you plan to deploy BACE as a Lambda application but do not want to connect to a DynamoDB instance, you can remove the `DynamoDBTable` resource specification and `DynamoDBCrudPolicy` from the AWS SAM `template.yaml`.

 ## DynamoDB

By default, this script is configured to create a DynamoDB table named `bace-db`, and all of the required functions to connect and interact with that table are configured here.
The typical user does not need to edit this script unless they want to change the DyanmoDB table name (from it's default value of `bace-db`).
If this is done, ensure that the `collection_or_table_name` variable matches the `TableName` property defined on line 23 of the `template.yaml` file.

## MongoDB

We have added support for connecting to a MongoDB database that is either hosted locally or hosted on MongoDB Atlas.

MongoDB provides a [series of guides](https://www.mongodb.com/docs/guides/) to help with common tasks.

If you plan to use MongoDB, make sure to uncomment the following lines in the `app/requirements.txt` file in order to read in the required Python packages.

```{}
# # MongoDB Requirements. Uncomment if using MongoDB
# pymongo==4.6.2
# dnspython==2.6.1
# certifi==2024.2.2
```

### MongoDB Local Connection

To connect to a local MongoDB instance, follow the following steps:

- Specify the name of your database (`db_name`) and table (`collection_or_table_name`) at the top of the document.
- Comment out the "Option 1" section used to define DynamoDB variables.
- Uncomment the "Option 2" section
- Update the `MONGO_URI` variable if your database is hosted at a different port than 27017.

These steps should allow you to connect to a locally hosted MongoDB database.

Resources for installing and setting up a local MongoDB instance with tutorials for different operating systems/platforms available at: [Install MongoDB](https://www.mongodb.com/docs/manual/installation/#std-label-tutorial-installation).

Note: it may be difficult to connect to a local MongoDB instancewhen testing your app with `sam local start-api`.

### MongoDB Atlas (Cloud Deployment)

[MongoDB Atlas](https://www.mongodb.com/) provides an option for deploying a cloud-based MongoDB database.

Once you have set up your MongoDB cluster, complete the following steps to connect your application to your database:

- Specify the name of your database (`db_name`) and table (`collection_or_table_name`) at the top of the document.
- Comment out the "Option 1" section used to define DynamoDB variables.
- Uncomment the "Option 3" section
- Specify your `mongo_username`, `mongo_password`, and `mongo_cluster` name within your environment (recommended) or in the document.
Be careful with hardcoding any sensitive information.

These steps should allow you to connect to a MongoDB instance hosted on the cloud via MongoDB Atlas

## Alternative Databases

Users may want to connect their application to an alternative database.
Update this file in order to interact with your preferred database.

Ensure that the `get_db_table`, `find_item`, `create_item`, and `update_item` are correctly defined and work with the specified inputs for each function.

These functions are read into `app/app.py` in order to ensure that an individual's data is retrieved and updated correctly.
If major changes are needed to accomodate these functions or additional variables must be passed to the functions to work correctly, the app script itself may need to be updated to incorporate these changes.

Additionaly, you may need to update `app/requirements.txt` with any additional Python packages needed to connect to an alternative database.

Note: Both DynamoDB and MongoDB are NoSQL databases that can more flexibily accomodate the dynamic information that is stored in BACE.
If you plan to use a SQL database, care should be taken to ensure that the new database is setup to store information from your user's profiles correctly.

## Conclusion

This document describes how to configure database connects within your `app/database/db.py` script.
We provide functions to connect your application to DynamoDB and MongoDB.
If you want to connect to another database, we list here the main functions that must be configured in order to integrate the `app/app.py` with your database.

# Creating a MongoDB Atlas Database

This page describes the steps for setting up a MongoDB database using [MongoDB Atlas](https://www.mongodb.com/).

For more detailed instructions on connecting to a MongoDB Atlas instance, see the instructions in "Configure Database (Optional)".
To create a MongoDB Atlas instance, and configure your BACE application to connect to it:

- Create an Atlas Account
- Create a new cluster.
- Create your BACE table
  - Create a new database (default to "BACE").
  - Create a new collection (default to "bace-db").
- Create a database user with permissions to read/write to your database and record the username and password.
- Follow the steps in "Configure Database (Optional)" to update `bace/database/db.py`.
Update the variables in this script with your chosen values
   - `db_name`: Name of your database
   - `collection_or_table_name`: Name of your collection
   - `mongo_cluster`: Name of your cluster
   - `mongo_username`: MongoDB Atlas username for account with database acess.
   - `mongo_password` : MongoDB Atlas password for account with database access.
   Be careful to store sensitive information securely.

Once you have stored these variables and followed the steps for configuring your database, your application will be connected to the MongoDB cloud instance.

You can run through a test survey and check your collection online to see your data updated in the database.

# Deployment Options

This page describes different ways that you can deploy your application.

Your app has two key components that need to be set up and hosted:

- a Flask application that handles API calls
- a database that stores user's information

The standard deployment uses AWS to host both your Flask application (via AWS Lambda) and your database (via DynamoDB).

The figure below describes this general framework.

[Insert hosting figure here]

Our AWS implementation was chosen because the serverless framework allows resources to scale easily when demand for your application increases.

However, there is no requirement that AWS services be used hosting either the app or the database.

## Alternative Methods for Hosting Flask Applications

The Flask documentation provides useful resources for deploying an application to production -- offering resources for self-hosting options and hosting platforms.
See [Flask: Deploying to Production](https://flask.palletsprojects.com/en/3.0.x/deploying/) for more details.

The application is setup by default to be hosted on AWS Lambda.
To prepare for hosting on another platform, you should update the `app/app.py` script and set `host_on_lambda` to `False` in order to set up your application as a general Flask app.
You will then deploy the app folder with `app/app.py` acting as the main Flask file.

We provide an example of how to host your app on PythonAnywhere in "Alternative Deployment Framework: PythonAnywhere/MongoDB".

It is beyond our scope to describe all methods for hosting a production-level Flask application, but the resources at the link above provide a useful starting point.

The main advantage of using AWS Lambda in our default setup is that Lambda is a serverless environment that allows compute resources to scale with demand.
This removes some of the burden on the user to ensure that required compute resources are available.
If you consider alternate hosting platforms that do not handle resource scaling themselves, make sure to use the load testing instructions to test that your setup handles the survey demand you expect.

## Alternative Database Options

By default, the application is set up to create and connect to an Amazon DynamoDB instance.
We also provide instructions and functions required to connect to a MongoDB instance.

See "Configure Database (Optional)" for more details on configuring alternate databases, and see "Alternative Deployment Framework: PythonAnywhere/MongoDB" for a walkthrough using MongoDB Atlas as the database.

The database you select stores information for each user and is updated as the respondent answers survey questions.
No computation is done within the database for the standard application, so any common database should work with a few caveats:

- Note that both DynamoDB and MongoDB are NoSQL databases that accept more flexible entries.
If you plan on using a SQL database (such as MySQL or PostgreSQL), you should take care to ensure that the information saved in a user's profile matches the schema for your destinataion table.
- You may need to update the `app/requirements.txt` if your chosen database requires additional packages to form connections.

## Conclusion

We designed BACE to be easy to deploy and use and hope the serverless framework built on AWS Lambda allows users to focus more on developing their application than on handling compute resources.
However, we want BACE to be flexible and easy to host using other methods.
Following the instructions here and in the associated walkthrough to deploy your app using the hosting platform/database that works best for your situation.

# Alternative Deployment Framework Walkthrough: PythonAnywhere/MongoDB

In this example, we walk you through the process for setting up a version of BACE that is hosted as a standard Flask app on PythonAnywhere and connects to a MongoDB Atlas database.

The `bace/app` folder functions as a normal Flask application.
Thus, you can host your application yourself on your own server or using a variety of hosting platforms (see the [Flask documentation](https://flask.palletsprojects.com/en/3.0.x/deploying/) for more details).

In this example, we will walk through setting up an application using PythonAnywhere, a low-cost and easy-to-use option.
The general steps and ideas will also be useful for setting up your application using other frameworks.

See the article [Setting up Flask application on PythonAnywhere](https://help.pythonanywhere.com/pages/Flask/) for up-to-date instructions and additional details.

## Preliminaries

Prior to beginning this walkthrough, complete the following steps:

- Set up MongoDB Atlas: This tutorial connects your BACE application to a database hosted on [MongoDB Atlas](https://www.mongodb.com/atlas/database).
Prior to starting this tutorial, create a MongoDB Atlas account and database.
Keep track of your credentials to allow for access.
See the "Creating a MongoDB Atlas Database" section for more details.
- Set up PythonAnywhere: Create a [PythonAnywhere](https://www.pythonanywhere.com/) account.
PythonAnywhere offers a free Beginner account that you can use to deploy a simple application and test out the service.
However, you will need a Hacker account (\$5/month) at minimum to deploy BACE.

## Create your application

Follow the steps below to create your application.

- Log in to your account.
Note to host a BACE application you need to create a Hacker account at a cost of \$5 per month.
- Open the "Web tab"
- Click "Add a new beb app".
  - (Optional) Set your web app’s domain name. By default, it will be hosted at `<user-name>.pythonanywhere.com`
- Select “Manual configuration” -> “Python 3.9” -> Next
- Open the “Consoles” tab and start a new “Bash” console.
- Clone the BACE repository to your: `git clone https://github.com/tt-econ/bace.git`
- Move into the bace directory: `cd bace`
- (Temporary while BACE-36 not on main)
  - Switch to BACE-36 branch `git switch BACE-36`
- Create a virtual environment and activate it: [How to use a virtualenv in your web app (to get newer versions of django, flask etc) | PythonAnywhere help](https://help.pythonanywhere.com/pages/Virtualenvs)
  - Run: `cd bace`
  - Run: `mkvirtualenv myvirtualenv --python=/usr/bin/python3.9`
  - Run `which python` to check whether this worked.
  This should return `/home/<user-name>/.virtualenvs/myvirtualenv/bin/python`
  - Activate using `workon myvirtualenv`
  - Install requirements `pip install -r app/requirements.txt`.
  This step may take a moment.
  Prior to running, ensure that the MongoDB requirements are uncommented in the `app/requirements.txt` file. (may take a moment)
- Exit the console and return to the Web tab
  - Click "Enter path to a virtualenv, if desired"
  - Type `myvirtualenv` or `/home/<user-name>/.virtualenvs/myvirtualenv` 
  - Under the code section, update the following:
    - Source code: `/home/<user-name>/bace/app/`
    - Working directory: `/home/<user-name>/bace/app/`
- Update the WSGI Configuration file
  - Click the link next to WSGI Configuration File
  - Scroll down and uncomment the Flask section to read the following

```{python}
import sys

# The "/home/<user-name>" below specifies your home
# directory -- the rest should be the directory you uploaded your Flask
# code to underneath the home directory.  So if you just ran
# "git clone git@github.com/myusername/myproject.git"
# ...or uploaded files to the directory "myproject", then you should
# specify "/home/<user-name>/myproject"
path = '/home/<user-name>/bace/app'
if path not in sys.path:
    sys.path.append(path)

from app import app as application  # noqa

```

- Save the file and return to the Web tab


(If you have already updated your database credentials, you can skip this step.)
To update your database credentials, complete the following steps:

- Return to the "Web" tab
- Under the Code section, click the "Go to directory" link to the right of Source code
- Click into "database/db.py"
- Update this file following the steps in "Configuring your database"
  - Comment out the DynamoDB Sections
  - Uncomment the MongoDB Atlas section and update your MongoDB connection credentials

```{python}
import pymongo
import certifi
import os

db_type = "mongodb"
mongodb_host = 'atlas'

# (Set username and password as environment variables on the machine/Lambda your function is operating on) or add them here.
mongo_username = "your_mongo_username" # os.environ.get('mongo_username')
mongo_password = "your_mongo_password" # os.environ.get('mongo_password')
mongo_cluster = "your_mongo_cluster" # os.environ.get('mongo_cluster') # The name of your cluster when setting up MongoDB Atlas


# The Mongo URI will be populated with your connection.
# Alternatively, Update the connection string directly. MongoDB Atlas -> Database -> Connect -> Drivers -> Copy and paste connection string here. Be careful not to share your passwords.
MONGO_URI = f"mongodb+srv://{mongo_username}:{mongo_password}@{mongo_cluster.lower()}.uukczpf.mongodb.net/?retryWrites=true&w=majority&appName={mongo_cluster}"

```

- Return to the "Web" tab and reload your application.
- Finally, go to https://<user-name>.pythonanywhere.com or your chosen domain name to find your application up and running
If you run into errors, you can access Log files from the Web dashboard
- We recommend testing your application by going to the "/survey" route.
You can run through an example survey to ensure all pages are loading as expected.
You can go to your online MongoDB Atlas collection to ensure that your data is being saved to the correct collection.

Note on Collaboration: PythonAnywhere works well with git.
Rather than editing code directly in PythonAnywhere, you should create your own BACE repository.
As you make changes to the repository and set up your own application locally/as a team, you should push these changes into the repo.
WithinPythonAnywhere, pull updates to the application.
To do this:

- Open the console
- cd into your repo
- pull changes git pull

Once you pull changes, refresh your web application, and your website will reflect the changes you made.
At this time multiple collaborators cannot work on the same URL endpoint.
However, research teams can use git to collaborate and make changes offline and then pull changes to PythonAnywhere from the account used to originally create the application.

### Python Anywhere Credentials

Details for setting up a `.env` file to handle your credentials are available [here](https://help.pythonanywhere.com/pages/environment-variables-for-web-apps/).
This is a useful option for setting credentials that can be referenced as environment variables so that passwords and other sensitive information is not hardcoded into your files.

- Install the dotenv package from a console: `pip install python-dotenv`
- Run commands to add credentials to your .env
  - Open Bash
  - CD into directory `cd ~/bace`
  - Run `echo “export MONGO_PASSWORD=<your-password>” >> .env` for MONGO_USERNAME, MONGO_PASSWORD, and MONGO_CLUSTER, specifying your credentials.

- Find and open the WSGI configuration file
- Add the following to the top of the file:

```
import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('~/bace')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))
```
Open the bace/app/database/db.py and save the following so that they reference the appropriate environment variables.

```
mongo_username = os.getenv("MONGO_USERNAME")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_cluster = os.getenv("MONGO_CLUSTER") 
```

Save the database file, and reload the app from the web tab

Now, your app can now be accessing MongoDB credentials from the .env file.


## Additional Resources

This walkthrough provides an example of how to host BACE using a different hosting platform and database.
There are many other ways to host a Flask application.
See [Flask's documentation](https://flask.palletsprojects.com/en/3.0.x/deploying/) for other options and follow the materials in the links there to setup your application.
We recommend using a hosting platform unless you are experienced and have experience setting up and managing your own server, as these platforms handle many of the details for deploying and managing your server.


