# Job-Board
Job Board is a platform where employers can post job listings, and candidates can apply for those positions.

## Running the app

### Run docker compose up -d --build
Recommend to use Docker to run the project. However, you will need to set up your mail username and password by setting the environment variable on Dockerfile.
Example of using GMAIL:<br />
    - MAIL_USERNAME=YOUR-EMAIL-ADDRESS<br />
    - MAIL_PASSWORD=YOUR-APP-PASSWORD-FOR-YOUR-GMAIL-ACCOUNT<br />
If it fails to connect to the database, try compose the database first and then flask_app after waiting for few seconds.

### Run python3 run.py
If you are using run.py you will need to manually set all the environment variable. Including the database.