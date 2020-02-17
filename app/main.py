import os
from datetime import datetime
from typing import Union

from dateutil.parser import isoparse
from peewee import fn, Case, DatabaseError, IntegrityError, ModelSelect
from sanic import Sanic
from sanic.log import logger
from sanic.response import empty, json
from sanic_openapi import doc, swagger_blueprint
from sanic_sentry import SanicSentry

from client import Client, ClientError
from models import db_setup, db_close, Match, Player

app = Sanic(name='gosu')
app.client = Client()
app.blueprint(swagger_blueprint)
sentry = SanicSentry(app)
WINRATE_PRECISION = os.environ.get('WINRATE_PRECISION', 2)


@app.listener('before_server_start')
async def setup_db(app, _):
    app.db = await db_setup()


@app.listener('before_server_stop')
async def close_db(app, _):
    await db_close()


@app.route('/match/<match_id:int>', methods=['POST'])
@doc.summary('Fetch and store match metadata to database')
@doc.description('Initiates fetch of Dota 2 match with corresponsing match_id '
                 'from API and stores obtained metadata to database.')
@doc.response(200, None, description='Metadata successfully stored')
@doc.response(400, None, description='Match is already in database')
@doc.response(503, None, description='Connection to Dota API failed')
@doc.response(500, None, description='Internal Server Error')
async def match_post(request, match_id: int):
    """Fetch and store match metadata to database."""
    try:
        match = app.client.fetch(match_id)
    except ClientError as exc:
        return empty(exc.status_code)
    with app.db.atomic() as transaction:
        try:
            match['start_time'] = datetime.fromtimestamp(match['start_time'])
            players = match.pop('players')
            Match.create(**match)
            for player in players:
                Player.create(match_id=match['match_id'], **player)
        except IntegrityError:
            transaction.rollback()
            return empty(400)
        except DatabaseError as exc:
            logger.exception('Error while saving metadata to db', exc_info=exc)
            transaction.rollback()
            return empty(500)
        return empty()


@app.route('/winrate/<hero_id>', methods=['GET'])
@doc.summary('Get winrate of the hero')
@doc.description('Calculates and returns winrate of the hero with hero_id '
                 'based on stored matches.')
@doc.consumes(
    doc.String(name="start", description="Games start time"),
    location="query",
    required=False)
@doc.response(
    200,
    {'winrate': float},
    description='Success. Winrate will be "null" if hero not found')
@doc.response(422, None, description='Invalid hero_id or start')
async def winrate_get(request, hero_id: str):
    """Get winrate of the hero."""
    try:
        hero_id = int(hero_id)
    except ValueError:
        return empty(422)
    query = create_winrate_query(hero_id)
    try:
        query = filter_start_time(query, request.args.get('start'))
    except ValueError:
        return empty(422)
    result = query.get()
    return json({'winrate': calculate_winrate(result.wins, result.matches)})


def create_winrate_query(hero_id: int) -> ModelSelect:
    """Query database for wins and matches of certain hero."""
    return Match.select(
        fn.COUNT(Match.match_id).alias('matches'),
        fn.SUM(Case(
            Match.radiant_win != Player.is_dire,
            ((True, 1), (False, 0)))
        ).alias('wins')
    ).join(Player).where((Player.hero_id == hero_id) & (Match.radiant_win.is_null(False)))


def filter_start_time(query: ModelSelect, start_time: str) -> ModelSelect:
    """Filter query by start_time of the matches."""
    return query.where(Match.start_time > isoparse(start_time)) if start_time else query


def calculate_winrate(wins: int, matches: int) -> Union[float, None]:
    """Calculate winrate or return None if there is no matches played."""
    return round(wins / matches, WINRATE_PRECISION) if matches > 0 else None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=os.environ.get('DEBUG'))
