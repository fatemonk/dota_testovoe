# Interview test

## What should you do

Write a python web-app that allows to fetch and store metadata for Dota 2 matches and provide basic statistics based on it.
Dota 2 is a competitive 5v5 team game. Each of 10 players plays a match for a distinct hero (described by integer `hero_id`). Sides are named **Radiant** and **Dire**.
Player side is determined by field `player_slot`: Slots [0:4] are Radiant, slots [128:132] are Dire. Each match has only one winner. `true` value of field `radiant_win` indicates win of the Radiant.
All these fields are available from [GetMatchDetails API](https://wiki.teamfortress.com/wiki/WebAPI/GetMatchDetails). Key for this api are provided in the `app/keys` file.

## Web-app specs

Result should be a Docker image with python web app that starts to listen for HTTP requests on port 8000 after a container start.
Docker container will be provided with environment variable `DATABASE_URL` that points to PostgreSQL 12 database like `postgres://user:password@host:port/database`.
On start application must create all needed tables in database and drop them on stop.

Web application must has 2 endpoints:
 - `/match/{match_id}` - handles only POST requests without body. Initiates fetch of Dota 2 match with corresponsing `match_id` from API and stores obtained metadata to database. Should response with successeful code and empty body on success and 400 if match is already in database.
 - `/winrate/{hero_id}` - handles only GET requests. Responses with winrate of the hero. winrate = "count of matches where provided hero was played by winner" / "total count of matches where provided hero was played". Should response with 200 with json response body `{"winrate": <float>}`. If there are no matches with this hero winrate should be `null`. Optionally, get-argument `start` can be provided with ISO 8601 time that indicates minimal start time of counted matches (should be compated against `start_time` field)
 - `/swagger` - OpenAPI documetation.

Application must be written using Python 3. Code style: flake8, max-line-length=130. Code should be written like a production-ready code that will be maintained and modified in the future.
Code should be in the /app directory. Also, you should provide Dockerfile that will be built
