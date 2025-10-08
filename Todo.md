Following the application from Task 1 and Task 2, please add the following features to the
application:
1. A Docker-based Postgres database to save information in the database instead of
in-memory. The same composer can be used for all services in the app.
2. Add the following endpoints to your application. Please choose any of the
appropriate HTTP methods (one of the GET, POST, PUT, PATCH, DELETE that you
think is suitable for this scenario) on each of the endpoints to deliver the requested
task.
a. Localhost:8000/users/
Use the appropriate HTTP method to update user information.
b. localhost:8000/admin/candidate
Use this endpoint to provide various functionalities with appropriate
methods for adding, updating, and deleting candidate information. The user
should be able to retrieve the vote counts for each candidate via a GET
request.
c. Localhost:8000/admin/candidate/{id}
Get the vote count for a specific candidate
d. Localhost:8000/users/vote
A user should be able to vote for a candidate by providing the candidate's ID
as part of the request body.
e. Localhost:8000/health
This should return a health message with status 200 and an ok message.
Imagine we have only one admin in the system, and we do not intend to have any more. The
admin can be authenticated using a preserved API token. You can use environmental
variables to save this token.
