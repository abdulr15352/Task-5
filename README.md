Task 3 for Abdul-Rafeh Alvi with email abal015@student.kristiania.no


## Environment Variables
You need to make a .env file with the following environment variables or choose your own:

- JWT_SECRET_KEY=abdul_secret_key 
- JWT_ALGORITHM=HS256
- JWT_EXPIRATION_MINUTES=1
- ADMIN_API_TOKEN=abdul_is_admin
- JWT_SECRET_KEY=abdul_secret_key
- JWT_ALGORITHM=HS256
- JWT_EXPIRATION_MINUTES=1
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=VeryStrongPassword
- POSTGRES_DB=voting_app_db
- POSTGRES_HOST=voting_db
- POSTGRES_PORT=5432

# How to run the app
## To build the image using Docker run the command:

- docker compose build

## To run the app with Docker run the command:
- docker compose up

## To stop the app from using Docker run the command:
- docker compose down

## If you also want to empty the databases:
- docker compose down -v


## Objectives
- Understand cloud computing fundamentals
- Explore endpoint management strategies
- Implement security best practices
