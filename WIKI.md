# CONTRIBUTING

## How to deal with database?
* create file `.env` in the root of the project
* set variable `DATABASE_URL` assigned with the link to database. To get link to a database create an instance of PostgreSQL database using hosting service (for example: [ElephantSQL](https://www.elephantsql.com/)).
***

## How to run Dockerfile locally?
```
docker run -dp 5005:5000 -w /app -v "$(pwd):/app" IMAGE_NAME sh -c "flask run --host 0.0.0.0"
```
### For Docker related details visit [Notion documentation](https://www.notion.so/sakalovami/Docker-55f4418bc2d141c7b491fccfbc18ccee).
***