import os

from peewee import (
    Model, BigIntegerField, BitField, BooleanField, DateTimeField,
    ForeignKeyField, IntegerField, SmallIntegerField,
)
from playhouse.db_url import connect

db = connect(os.environ.get('DATABASE_URL'))


class BaseModel(Model):

    class Meta:
        database = db

    @classmethod
    def create(cls, *args, **kwargs):
        return super().create(
            *args, **{k: v for k, v in kwargs.items() if k in cls._meta.fields})


class Match(BaseModel):
    """Match metadata."""
    match_id = BigIntegerField(primary_key=True)
    radiant_win = BooleanField(null=True)
    duration = IntegerField(null=True)
    pre_game_duration = IntegerField(null=True)
    season = SmallIntegerField(null=True)
    start_time = DateTimeField(null=True)
    match_seq_num = BigIntegerField(null=True)
    tower_status_radiant = BitField(null=True)
    tower_status_dire = BitField(null=True)
    barracks_status_radiant = BitField(null=True)
    barracks_status_dire = BitField(null=True)
    cluster = IntegerField(null=True)
    first_blood_time = IntegerField(null=True)
    lobby_type = SmallIntegerField(null=True)
    human_players = SmallIntegerField(null=True)
    leagueid = IntegerField(null=True)
    positive_votes = SmallIntegerField(null=True)
    negative_votes = SmallIntegerField(null=True)
    game_mode = SmallIntegerField(null=True)
    flags = BitField(null=True)
    engine = SmallIntegerField(null=True)
    radiant_score = IntegerField(null=True)
    dire_score = IntegerField(null=True)


class Player(BaseModel):
    """Player metadata from certain match."""
    match_id = ForeignKeyField(Match, backref='players')
    account_id = BigIntegerField(null=True)
    player_slot = BitField(null=True)
    hero_id = SmallIntegerField(null=True)
    item_0 = SmallIntegerField(null=True)
    item_1 = SmallIntegerField(null=True)
    item_2 = SmallIntegerField(null=True)
    item_3 = SmallIntegerField(null=True)
    item_4 = SmallIntegerField(null=True)
    item_5 = SmallIntegerField(null=True)
    backpack_0 = SmallIntegerField(null=True)
    backpack_1 = SmallIntegerField(null=True)
    backpack_2 = SmallIntegerField(null=True)
    item_neutral = SmallIntegerField(null=True)
    kills = SmallIntegerField(null=True)
    deaths = SmallIntegerField(null=True)
    assists = SmallIntegerField(null=True)
    leaver_status = SmallIntegerField(null=True)
    last_hits = SmallIntegerField(null=True)
    denies = SmallIntegerField(null=True)
    gold_per_min = IntegerField(null=True)
    xp_per_min = IntegerField(null=True)
    level = SmallIntegerField(null=True)
    hero_damage = IntegerField(null=True)
    tower_damage = IntegerField(null=True)
    hero_healing = IntegerField(null=True)
    gold = IntegerField(null=True)
    gold_spent = IntegerField(null=True)
    scaled_hero_damage = IntegerField(null=True)
    scaled_tower_damage = IntegerField(null=True)
    scaled_hero_healing = IntegerField(null=True)
    is_dire = player_slot.flag(128)


tables = [Match, Player]


async def db_setup():
    db.connect()
    db.create_tables(tables)
    return db


async def db_close():
    db.drop_tables(tables)
