"""Db schema definitions and setup routines."""

import sqlalchemy as sa
from sqlalchemy.sql import text as sql_text
from sqlalchemy.types import SMALLINT
from sqlalchemy.types import CHAR
from sqlalchemy.types import VARCHAR
from sqlalchemy.types import TEXT
from sqlalchemy.types import BOOLEAN

#pylint: disable=line-too-long, too-many-lines, bad-whitespace

# [DK] we changed and removed some tables so i upgraded DB_VERSION to 18
DB_VERSION = 18

def build_metadata():
    """Build schema def with SqlAlchemy"""
    metadata = sa.MetaData()

    sa.Table(
        'hive_blocks', metadata,
        sa.Column('num', sa.Integer, primary_key=True, autoincrement=False),
        sa.Column('hash', CHAR(40), nullable=False),
        sa.Column('prev', CHAR(40)),
        sa.Column('txs', SMALLINT, server_default='0', nullable=False),
        sa.Column('ops', SMALLINT, server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),

        sa.UniqueConstraint('hash', name='hive_blocks_ux1'),
        sa.ForeignKeyConstraint(['prev'], ['hive_blocks.hash'], name='hive_blocks_fk1'),
    )

    sa.Table(
        'hive_accounts', metadata,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', VARCHAR(16), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        #sa.Column('block_num', sa.Integer, nullable=False),
        sa.Column('reputation', sa.Float(precision=6), nullable=False, server_default='25'),

        sa.Column('display_name', sa.String(20)),
        sa.Column('about', sa.String(160)),
        sa.Column('location', sa.String(30)),
        sa.Column('website', sa.String(1024)),
        sa.Column('profile_image', sa.String(1024), nullable=False, server_default=''),
        sa.Column('cover_image', sa.String(1024), nullable=False, server_default=''),

        sa.Column('followers', sa.Integer, nullable=False, server_default='0'),
        sa.Column('following', sa.Integer, nullable=False, server_default='0'),

        sa.Column('proxy', VARCHAR(16), nullable=False, server_default=''),
        sa.Column('post_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('proxy_weight', sa.Float(precision=6), nullable=False, server_default='0'),
        sa.Column('vote_weight', sa.Float(precision=6), nullable=False, server_default='0'),
        sa.Column('kb_used', sa.Integer, nullable=False, server_default='0'), # deprecated
        sa.Column('rank', sa.Integer, nullable=False, server_default='0'),

        sa.Column('lastread_at', sa.DateTime, nullable=False, server_default='1970-01-01 00:00:00'),
        sa.Column('active_at', sa.DateTime, nullable=False, server_default='1970-01-01 00:00:00'),
        sa.Column('cached_at', sa.DateTime, nullable=False, server_default='1970-01-01 00:00:00'),
        sa.Column('raw_json', sa.Text),


        sa.UniqueConstraint('name', name='hive_accounts_ux1'),
        sa.Index('hive_accounts_ix1', 'vote_weight', 'id'), # core: quick ranks
        sa.Index('hive_accounts_ix2', 'name', 'id'), # core: quick id map
        sa.Index('hive_accounts_ix3', 'vote_weight', 'name', postgresql_ops=dict(name='varchar_pattern_ops')), # API: lookup
        sa.Index('hive_accounts_ix4', 'id', 'name'), # API: quick filter/sort
        sa.Index('hive_accounts_ix5', 'cached_at', 'name'), # core/listen sweep
    )

    sa.Table(
        'hive_posts', metadata,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('parent_id', sa.Integer),
        sa.Column('root_id', sa.Integer, nullable=False, server_defaut='-1'), # -1 will mean no root, root_author_id = author_id and root_permlink_id = permlink_id
        sa.Column('author_id', sa.Integer, nullable=False),
        sa.Column('permlink_id', sa.BigInteger, nullable=False),
        sa.Column('category_id', sa.Integer, nullable=False),
        sa.Column('community_id', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('depth', SMALLINT, nullable=False),
        sa.Column('is_deleted', BOOLEAN, nullable=False, server_default='0'),
        sa.Column('is_pinned', BOOLEAN, nullable=False, server_default='0'),
        sa.Column('is_muted', BOOLEAN, nullable=False, server_default='0'),
        sa.Column('is_valid', BOOLEAN, nullable=False, server_default='1'),
        sa.Column('promoted', sa.types.DECIMAL(10, 3), nullable=False, server_default='0'),

        sa.Column('children', SMALLINT, nullable=False, server_default='0'),

        # basic/extended-stats
        sa.Column('author_rep', sa.Float(precision=6), nullable=False, server_default='0'),
        sa.Column('flag_weight', sa.Float(precision=6), nullable=False, server_default='0'),
        sa.Column('total_votes', sa.Integer, nullable=False, server_default='0'),
        sa.Column('up_votes', sa.Integer, nullable=False, server_default='0'),

        # core stats/indexes
        sa.Column('payout', sa.types.DECIMAL(10, 3), nullable=False, server_default='0'),
        sa.Column('payout_at', sa.DateTime, nullable=False, server_default='1990-01-01'),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default='1990-01-01'),
        sa.Column('is_paidout', BOOLEAN, nullable=False, server_default='0'),

        # ui flags/filters
        sa.Column('is_nsfw', BOOLEAN, nullable=False, server_default='0'),
        sa.Column('is_declined', BOOLEAN, nullable=False, server_default='0'),
        sa.Column('is_full_power', BOOLEAN, nullable=False, server_default='0'),
        sa.Column('is_hidden', BOOLEAN, nullable=False, server_default='0'),
        sa.Column('is_grayed', BOOLEAN, nullable=False, server_default='0'),

        # important indexes
        sa.Column('rshares', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('sc_trend', sa.Float(precision=6), nullable=False, server_default='0'),
        sa.Column('sc_hot', sa.Float(precision=6), nullable=False, server_default='0'),

        sa.Column('total_payout_value', sa.String(30), nullable=False, server_default=''),
        sa.Column('author_rewards', sa.BigInteger, nullable=False, server_default='0'),

        sa.Column('author_rewards_hive', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('author_rewards_hbd', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('author_rewards_vests', sa.BigInteger, nullable=False, server_default='0'),

        sa.Column('children_abs_rshares', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('abs_rshares', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('vote_rshares', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('net_votes', sa.Integer, nullable=False, server_default='0'),
        sa.Column('active', sa.DateTime, nullable=False, server_default='1970-01-01 00:00:00'),
        sa.Column('last_payout', sa.DateTime, nullable=False, server_default='1970-01-01 00:00:00'),
        sa.Column('cashout_time', sa.DateTime, nullable=False, server_default='1970-01-01 00:00:00'),
        sa.Column('max_cashout_time', sa.DateTime, nullable=False, server_default='1970-01-01 00:00:00'),
        sa.Column('percent_hbd', sa.Integer, nullable=False, server_default='0'),
        sa.Column('reward_weight', sa.Integer, nullable=False, server_default='0'),

        sa.Column('parent_author_id', sa.Integer, nullable=False),
        sa.Column('parent_permlink_id', sa.BigInteger, nullable=False),
        sa.Column('curator_payout_value', sa.String(30), nullable=False, server_default=''),
        sa.Column('root_author_id', sa.Integer, nullable=False),
        sa.Column('root_permlink_id', sa.BigInteger, nullable=False),
        sa.Column('max_accepted_payout',  sa.String(30), nullable=False, server_default=''),
        sa.Column('percent_steem_dollars', sa.Integer, nullable=False, server_default='-1'),
        sa.Column('allow_replies', BOOLEAN, nullable=False, server_default='1'),
        sa.Column('allow_votes', BOOLEAN, nullable=False, server_default='1'),
        sa.Column('allow_curation_rewards', BOOLEAN, nullable=False, server_default='1'),
        sa.Column('beneficiaries', sa.JSON, nullable=False, server_default='[]'),
        sa.Column('url', sa.Text, nullable=False, server_default=''),
        sa.Column('root_title', sa.String(255), nullable=False, server_default=''),

        sa.ForeignKeyConstraint(['author_id'], ['hive_accounts.id'], name='hive_posts_fk1'),
        sa.ForeignKeyConstraint(['parent_id'], ['hive_posts.id'], name='hive_posts_fk3'),
        sa.UniqueConstraint('author_id', 'permlink_id', name='hive_posts_ux1'),
        sa.Index('hive_posts_ix3', 'author_id', 'depth', 'id', postgresql_where=sql_text("is_deleted = '0'")), # API: author blog/comments
        sa.Index('hive_posts_ix5', 'id', postgresql_where=sql_text("is_pinned = '1' AND is_deleted = '0'")), # API: pinned post status
        sa.Index('hive_posts_depth_idx', 'depth'),
        sa.Index('hive_posts_parent_id_idx', 'parent_id'),
        sa.Index('hive_posts_community_id_idx', 'community_id'),

        sa.Index('hive_posts_category_id_idx', 'category_id'),
        sa.Index('hive_posts_payout_at_idx', 'payout_at'),
        sa.Index('hive_posts_payout_at_idx2', 'payout_at', postgresql_where=sql_text("is_paidout = '0'")),
        sa.Index('hive_posts_payout_idx', 'payout'),
        sa.Index('hive_posts_promoted_idx', 'promoted'),
        sa.Index('hive_posts_sc_trend_idx', 'sc_trend'),
        sa.Index('hive_posts_sc_hot_idx', 'sc_hot'),
        sa.Index('hive_posts_created_at_idx', 'created_at'),
        sa.UniqueConstraint('author_id', 'permlink_id', name='hive_posts_ux1')
    )

    sa.Table(
        'hive_post_data', metadata,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=False),
        sa.Column('title', VARCHAR(255), nullable=False),
        sa.Column('preview', VARCHAR(1024), nullable=False),
        sa.Column('img_url', VARCHAR(1024), nullable=False),
        sa.Column('body', TEXT),
        sa.Column('json', TEXT)
    )

    sa.Table(
        'hive_permlink_data', metadata,
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('permlink', sa.String(255), nullable=False),
        sa.UniqueConstraint('permlink', name='hive_permlink_data_permlink')
    )

    sa.Table(
        'hive_category_data', metadata,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('category', sa.String(255), nullable=False),
        sa.UniqueConstraint('category', name='hive_category_data_category')
    )

    sa.Table(
        'hive_votes', metadata,
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('post_id', sa.Integer, nullable=False),
        sa.Column('voter_id', sa.Integer, nullable=False),
        sa.Column('author_id', sa.Integer, nullable=False),
        sa.Column('permlink_id', sa.Integer, nullable=False),
        sa.Column('weight', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('rshares', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('vote_percent', sa.Integer, server_default='0'),
        sa.Column('last_update', sa.DateTime, nullable=False, server_default='1970-01-01 00:00:00'),
        sa.Column('num_changes', sa.Integer, server_default='0'), 

        sa.ForeignKeyConstraint(['post_id'], ['hive_posts.id']),
        sa.ForeignKeyConstraint(['voter_id'], ['hive_accounts.id']),
        sa.ForeignKeyConstraint(['author_id'], ['hive_accounts.id']),
        sa.ForeignKeyConstraint(['permlink_id'], ['hive_permlink_data.id']),

        sa.Index('hive_votes_post_id_idx', 'post_id'),
        sa.Index('hive_votes_voter_id_idx', 'voter_id'),
        sa.Index('hive_votes_author_id_idx', 'author_id'),
        sa.Index('hive_votes_permlink_id_idx', 'permlink_id'),
        sa.Index('hive_votes_upvote_idx', 'vote_percent', postgresql_where=sql_text("vote_percent > 0")),
        sa.Index('hive_votes_downvote_idx', 'vote_percent', postgresql_where=sql_text("vote_percent < 0"))
    )

    sa.Table(
        'hive_post_tags', metadata,
        sa.Column('post_id', sa.Integer, nullable=False),
        sa.Column('tag', sa.String(32), nullable=False),
        sa.UniqueConstraint('tag', 'post_id', name='hive_post_tags_ux1'), # core
        sa.Index('hive_post_tags_ix1', 'post_id'), # core
    )

    sa.Table(
        'hive_follows', metadata,
        sa.Column('follower', sa.Integer, nullable=False),
        sa.Column('following', sa.Integer, nullable=False),
        sa.Column('state', SMALLINT, nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime, nullable=False),

        sa.UniqueConstraint('following', 'follower', name='hive_follows_ux3'), # core
        sa.Index('hive_follows_ix5a', 'following', 'state', 'created_at', 'follower'),
        sa.Index('hive_follows_ix5b', 'follower', 'state', 'created_at', 'following'),
    )

    sa.Table(
        'hive_reblogs', metadata,
        sa.Column('account', VARCHAR(16), nullable=False),
        sa.Column('post_id', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),

        sa.ForeignKeyConstraint(['account'], ['hive_accounts.name'], name='hive_reblogs_fk1'),
        sa.ForeignKeyConstraint(['post_id'], ['hive_posts.id'], name='hive_reblogs_fk2'),
        sa.UniqueConstraint('account', 'post_id', name='hive_reblogs_ux1'), # core
        sa.Index('hive_reblogs_ix1', 'post_id', 'account', 'created_at'), # API -- not yet used
    )

    sa.Table(
        'hive_payments', metadata,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('block_num', sa.Integer, nullable=False),
        sa.Column('tx_idx', SMALLINT, nullable=False),
        sa.Column('post_id', sa.Integer, nullable=False),
        sa.Column('from_account', sa.Integer, nullable=False),
        sa.Column('to_account', sa.Integer, nullable=False),
        sa.Column('amount', sa.types.DECIMAL(10, 3), nullable=False),
        sa.Column('token', VARCHAR(5), nullable=False),

        sa.ForeignKeyConstraint(['from_account'], ['hive_accounts.id'], name='hive_payments_fk1'),
        sa.ForeignKeyConstraint(['to_account'], ['hive_accounts.id'], name='hive_payments_fk2'),
        sa.ForeignKeyConstraint(['post_id'], ['hive_posts.id'], name='hive_payments_fk3'),
    )

    sa.Table(
        'hive_feed_cache', metadata,
        sa.Column('post_id', sa.Integer, nullable=False),
        sa.Column('account_id', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.UniqueConstraint('post_id', 'account_id', name='hive_feed_cache_ux1'), # core
        sa.Index('hive_feed_cache_ix1', 'account_id', 'post_id', 'created_at'), # API (and rebuild?)
    )

    sa.Table(
        'hive_state', metadata,
        sa.Column('block_num', sa.Integer, primary_key=True, autoincrement=False),
        sa.Column('db_version', sa.Integer, nullable=False),
        sa.Column('steem_per_mvest', sa.types.DECIMAL(14, 6), nullable=False),
        sa.Column('usd_per_steem', sa.types.DECIMAL(14, 6), nullable=False),
        sa.Column('sbd_per_steem', sa.types.DECIMAL(14, 6), nullable=False),
        sa.Column('dgpo', sa.Text, nullable=False),
    )

    metadata = build_metadata_community(metadata)

    return metadata

def build_metadata_community(metadata=None):
    """Build community schema defs"""
    if not metadata:
        metadata = sa.MetaData()

    sa.Table(
        'hive_communities', metadata,
        sa.Column('id',          sa.Integer,      primary_key=True, autoincrement=False),
        sa.Column('type_id',     SMALLINT,        nullable=False),
        sa.Column('lang',        CHAR(2),         nullable=False, server_default='en'),
        sa.Column('name',        VARCHAR(16),     nullable=False),
        sa.Column('title',       sa.String(32),   nullable=False, server_default=''),
        sa.Column('created_at',  sa.DateTime,     nullable=False),
        sa.Column('sum_pending', sa.Integer,      nullable=False, server_default='0'),
        sa.Column('num_pending', sa.Integer,      nullable=False, server_default='0'),
        sa.Column('num_authors', sa.Integer,      nullable=False, server_default='0'),
        sa.Column('rank',        sa.Integer,      nullable=False, server_default='0'),
        sa.Column('subscribers', sa.Integer,      nullable=False, server_default='0'),
        sa.Column('is_nsfw',     BOOLEAN,         nullable=False, server_default='0'),
        sa.Column('about',       sa.String(120),  nullable=False, server_default=''),
        sa.Column('primary_tag', sa.String(32),   nullable=False, server_default=''),
        sa.Column('category',    sa.String(32),   nullable=False, server_default=''),
        sa.Column('avatar_url',  sa.String(1024), nullable=False, server_default=''),
        sa.Column('description', sa.String(5000), nullable=False, server_default=''),
        sa.Column('flag_text',   sa.String(5000), nullable=False, server_default=''),
        sa.Column('settings',    TEXT,            nullable=False, server_default='{}'),

        sa.UniqueConstraint('name', name='hive_communities_ux1'),
        sa.Index('hive_communities_ix1', 'rank', 'id')
    )

    sa.Table(
        'hive_roles', metadata,
        sa.Column('account_id',   sa.Integer,     nullable=False),
        sa.Column('community_id', sa.Integer,     nullable=False),
        sa.Column('created_at',   sa.DateTime,    nullable=False),
        sa.Column('role_id',      SMALLINT,       nullable=False, server_default='0'),
        sa.Column('title',        sa.String(140), nullable=False, server_default=''),

        sa.UniqueConstraint('account_id', 'community_id', name='hive_roles_ux1'),
        sa.Index('hive_roles_ix1', 'community_id', 'account_id', 'role_id'),
    )

    sa.Table(
        'hive_subscriptions', metadata,
        sa.Column('account_id',   sa.Integer,  nullable=False),
        sa.Column('community_id', sa.Integer,  nullable=False),
        sa.Column('created_at',   sa.DateTime, nullable=False),

        sa.UniqueConstraint('account_id', 'community_id', name='hive_subscriptions_ux1'),
        sa.Index('hive_subscriptions_ix1', 'community_id', 'account_id', 'created_at'),
    )

    sa.Table(
        'hive_notifs', metadata,
        sa.Column('id',           sa.Integer,  primary_key=True),
        sa.Column('type_id',      SMALLINT,    nullable=False),
        sa.Column('score',        SMALLINT,    nullable=False),
        sa.Column('created_at',   sa.DateTime, nullable=False),
        sa.Column('src_id',       sa.Integer,  nullable=True),
        sa.Column('dst_id',       sa.Integer,  nullable=True),
        sa.Column('post_id',      sa.Integer,  nullable=True),
        sa.Column('community_id', sa.Integer,  nullable=True),
        sa.Column('block_num',    sa.Integer,  nullable=True),
        sa.Column('payload',      sa.Text,     nullable=True),

        sa.Index('hive_notifs_ix1', 'dst_id',                  'id', postgresql_where=sql_text("dst_id IS NOT NULL")),
        sa.Index('hive_notifs_ix2', 'community_id',            'id', postgresql_where=sql_text("community_id IS NOT NULL")),
        sa.Index('hive_notifs_ix3', 'community_id', 'type_id', 'id', postgresql_where=sql_text("community_id IS NOT NULL")),
        sa.Index('hive_notifs_ix4', 'community_id', 'post_id', 'type_id', 'id', postgresql_where=sql_text("community_id IS NOT NULL AND post_id IS NOT NULL")),
        sa.Index('hive_notifs_ix5', 'post_id', 'type_id', 'dst_id', 'src_id', postgresql_where=sql_text("post_id IS NOT NULL AND type_id IN (16,17)")), # filter: dedupe
        sa.Index('hive_notifs_ix6', 'dst_id', 'created_at', 'score', 'id', postgresql_where=sql_text("dst_id IS NOT NULL")), # unread
    )

    return metadata


def teardown(db):
    """Drop all tables"""
    build_metadata().drop_all(db.engine())

def setup(db):
    """Creates all tables and seed data"""
    # initialize schema
    build_metadata().create_all(db.engine())

    # tune auto vacuum/analyze
    reset_autovac(db)

    # default rows
    sqls = [
        "INSERT INTO hive_state (block_num, db_version, steem_per_mvest, usd_per_steem, sbd_per_steem, dgpo) VALUES (0, %d, 0, 0, 0, '')" % DB_VERSION,
        "INSERT INTO hive_blocks (num, hash, created_at) VALUES (0, '0000000000000000000000000000000000000000', '2016-03-24 16:04:57')",

        "INSERT INTO hive_permlink_data (id, permlink) VALUES (0, '')",
        "INSERT INTO hive_category_data (id, category) VALUES (0, '')",
        "INSERT INTO hive_accounts (id, name, created_at) VALUES (0, '', '1990-01-01T00:00:00')",

        "INSERT INTO hive_accounts (name, created_at) VALUES ('miners',    '2016-03-24 16:05:00')",
        "INSERT INTO hive_accounts (name, created_at) VALUES ('null',      '2016-03-24 16:05:00')",
        "INSERT INTO hive_accounts (name, created_at) VALUES ('temp',      '2016-03-24 16:05:00')",
        "INSERT INTO hive_accounts (name, created_at) VALUES ('initminer', '2016-03-24 16:05:00')",

        """INSERT INTO public.hive_posts(
          id, parent_id, root_id, author_id, permlink_id, category_id, community_id, parent_author_id, parent_permlink_id, root_author_id, root_permlink_id, created_at, depth)
          VALUES (0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, now(), 0);"""]
    for sql in sqls:
        db.query(sql)

    sql = "CREATE INDEX hive_communities_ft1 ON hive_communities USING GIN (to_tsvector('english', title || ' ' || about))"
    db.query(sql)

    sql = """
DROP FUNCTION if exists add_hive_post(character varying,character varying,character varying,character varying,timestamp without time zone,timestamp without time zone)
;
CREATE OR REPLACE FUNCTION add_hive_post(
  in _author hive_accounts.name%TYPE,
  in _permlink hive_permlink_data.permlink%TYPE,
  in _parent_author hive_accounts.name%TYPE,
  in _parent_permlink hive_permlink_data.permlink%TYPE,
  in _date hive_posts.created_at%TYPE,
  in _community_support_start_date hive_posts.created_at%TYPE)
RETURNS TABLE (id hive_posts.id%TYPE, author_id hive_posts.author_id%TYPE, permlink_id hive_posts.permlink_id%TYPE,
               parent_id hive_posts.parent_id%TYPE, community_id hive_posts.community_id%TYPE,
               is_valid hive_posts.is_valid%TYPE, is_muted hive_posts.is_muted%TYPE, depth hive_posts.depth%TYPE)
LANGUAGE plpgsql
AS
$function$
BEGIN

INSERT INTO hive_permlink_data
(permlink)
values
(
_permlink
)
ON CONFLICT DO NOTHING
;
if _parent_author != '' THEN
  RETURN QUERY INSERT INTO hive_posts 
  (parent_id, root_id, parent_author_id, parent_permlink_id, depth, community_id,
   category_id,
   root_author_id, root_permlink_id,
   is_muted, is_valid,
   author_id, permlink_id, created_at)
  SELECT 
      php.id AS parent_id, 
      (SELECT
        CASE 
          WHEN root_id=-1 THEN php.id
          ELSE root_id
       FROM hive_posts
       WHERE hive_posts.id=php.id
      ) as root_id,
      php.author_id as parent_author_id,
      php.permlink_id as parent_permlink_id, php.depth + 1 as depth,
      (CASE
      WHEN _date > _community_support_start_date THEN
        COALESCE(php.community_id, (select hc.id from hive_communities hc where hc.name = _parent_permlink))
      ELSE NULL
    END)  as community_id,
      COALESCE(php.category_id, (select hcg.id from hive_category_data hcg where hcg.category = _parent_permlink)) as category_id,
      php.root_author_id as root_author_id, 
      php.root_permlink_id as root_permlink_id, 
      php.is_muted as is_muted, php.is_valid as is_valid,
      ha.id as author_id, hpd.id as permlink_id, _date as created_at
  FROM hive_accounts ha,
       hive_permlink_data hpd,
       hive_posts php
  INNER JOIN hive_accounts pha ON pha.id = php.author_id
  INNER JOIN hive_permlink_data phpd ON phpd.id = php.permlink_id
  WHERE pha.name = _parent_author and phpd.permlink = _parent_permlink AND
         ha.name = _author and hpd.permlink = _permlink 
  RETURNING hive_posts.id, hive_posts.author_id, hive_posts.permlink_id, hive_posts.parent_id, hive_posts.community_id, hive_posts.is_valid, hive_posts.is_muted, hive_posts.depth
;
ELSE
  INSERT INTO hive_category_data
  (category) 
  VALUES (_parent_permlink) 
  ON CONFLICT (category) DO NOTHING
  ;

  RETURN QUERY INSERT INTO hive_posts 
  (parent_id, root_id, parent_author_id, parent_permlink_id, depth, community_id,
   category_id,
   root_author_id, root_permlink_id,
   is_muted, is_valid,
   author_id, permlink_id, created_at)
  SELECT 0 AS parent_id, -1 AS root_id, 0 as parent_author_id, 0 as parent_permlink_id, 0 as depth,
      (CASE
        WHEN _date > _community_support_start_date THEN
          (select hc.id from hive_communities hc where hc.name = _parent_permlink)
        ELSE NULL
      END)  as community_id,
      (select hcg.id from hive_category_data hcg where hcg.category = _parent_permlink) as category_id,
      ha.id as root_author_id, -- use author_id as root one if no parent
      hpd.id as root_permlink_id, -- use perlink_id as root one if no parent
      false as is_muted, true as is_valid,
      ha.id as author_id, hpd.id as permlink_id, _date as created_at
  FROM hive_accounts ha,
       hive_permlink_data hpd
  WHERE ha.name = _author and hpd.permlink = _permlink 
  RETURNING hive_posts.id, hive_posts.author_id, hive_posts.permlink_id, hive_posts.parent_id, hive_posts.community_id, hive_posts.is_valid, hive_posts.is_muted, hive_posts.depth;
END IF;
END
$function$
    """
    db.query_row(sql)

def reset_autovac(db):
    """Initializes/resets per-table autovacuum/autoanalyze params.

    We use a scale factor of 0 and specify exact threshold tuple counts,
    per-table, in the format (autovacuum_threshold, autoanalyze_threshold)."""

    autovac_config = { #    vacuum  analyze
        'hive_accounts':    (50000, 100000),
        'hive_posts':       (2500, 10000),
        'hive_post_tags':   (5000, 10000),
        'hive_follows':     (5000, 5000),
        'hive_feed_cache':  (5000, 5000),
        'hive_blocks':      (5000, 25000),
        'hive_reblogs':     (5000, 5000),
        'hive_payments':    (5000, 5000),
    }

    for table, (n_vacuum, n_analyze) in autovac_config.items():
        sql = """ALTER TABLE %s SET (autovacuum_vacuum_scale_factor = 0,
                                     autovacuum_vacuum_threshold = %s,
                                     autovacuum_analyze_scale_factor = 0,
                                     autovacuum_analyze_threshold = %s)"""
        db.query(sql % (table, n_vacuum, n_analyze))
