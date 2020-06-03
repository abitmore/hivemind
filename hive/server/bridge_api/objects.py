"""Handles building condenser-compatible response objects."""

import logging
import ujson as json
from hive.server.common.mutes import Mutes
from hive.server.common.helpers import json_date

from hive.utils.normalize import sbd_amount

log = logging.getLogger(__name__)

# pylint: disable=too-many-lines

async def load_profiles(db, names):
    """`get_accounts`-style lookup for `get_state` compat layer."""
    sql = """SELECT id, name, display_name, about, reputation, vote_weight,
                    created_at, post_count, profile_image, location, website,
                    cover_image, rank, following, followers, active_at
               FROM hive_accounts WHERE name IN :names"""
    rows = await db.query_all(sql, names=tuple(names))
    return [_condenser_profile_object(row) for row in rows]

async def load_posts_reblogs(db, ids_with_reblogs, truncate_body=0):
    """Given a list of (id, reblogged_by) tuples, return posts w/ reblog key."""
    post_ids = [r[0] for r in ids_with_reblogs]
    reblog_by = dict(ids_with_reblogs)
    posts = await load_posts(db, post_ids, truncate_body=truncate_body)

    # Merge reblogged_by data into result set
    for post in posts:
        rby = set(reblog_by[post['post_id']].split(','))
        rby.discard(post['author'])
        if rby:
            post['reblogged_by'] = list(rby)

    return posts

ROLES = {-2: 'muted', 0: 'guest', 2: 'member', 4: 'mod', 6: 'admin', 8: 'owner'}

async def load_posts_keyed(db, ids, truncate_body=0):
    """Given an array of post ids, returns full posts objects keyed by id."""
    # pylint: disable=too-many-locals
    assert ids, 'no ids passed to load_posts_keyed'

    # fetch posts and associated author reps
    sql = """
        SELECT hp.id, 
            community_id, 
            ha_a.name as author,
            hpd_p.permlink as permlink,
            hpd.title as title, 
            hpd.body as body, 
            hcd.category as category, 
            depth,
            promoted, 
            payout, 
            payout_at, 
            is_paidout, 
            children, 
            hpd.votes as votes,
            hp.created_at, 
            updated_at, 
            rshares, 
            hpd.json as json,
            is_hidden, 
            is_grayed, 
            total_votes, 
            flag_weight,
            ha_pa.name as parent_author,
            hpd_pp.permlink as parent_permlink,
            curator_payout_value, 
            ha_ra.name as root_author,
            hpd_rp.permlink as root_permlink,
            max_accepted_payout, 
            percent_steem_dollars, 
            allow_replies, 
            allow_votes, 
            allow_curation_rewards, 
            beneficiaries, 
            url, 
            root_title
        FROM hive_posts hp
        LEFT JOIN hive_accounts ha_a ON ha_a.id = hp.author_id
        LEFT JOIN hive_permlink_data hpd_p ON hpd_p.id = hp.permlink_id
        LEFT JOIN hive_post_data hpd ON hpd.id = hp.id
        LEFT JOIN hive_category_data hcd ON hcd.id = hp.category_id
        LEFT JOIN hive_accounts ha_pa ON ha_pa.id = hp.parent_author_id
        LEFT JOIN hive_permlink_data hpd_pp ON hpd_pp.id = hp.parent_permlink_id
        LEFT JOIN hive_accounts ha_ra ON ha_ra.id = hp.root_author_id
        LEFT JOIN hive_permlink_data hpd_rp ON hpd_rp.id = hp.root_permlink_id
        WHERE id IN :ids
    """
    result = await db.query_all(sql, ids=tuple(ids))
    author_map = await _query_author_map(db, result)

    # TODO: author affiliation?
    ctx = {}
    posts_by_id = {}
    author_ids = {}
    post_cids = {}
    for row in result:
        row = dict(row)
        author = author_map[row['author']]
        author_ids[author['id']] = author['name']

        row['author_rep'] = author['reputation']
        post = _condenser_post_object(row, truncate_body=truncate_body)

        post['blacklists'] = Mutes.lists(post['author'], author['reputation'])

        posts_by_id[row['post_id']] = post
        post_cids[row['post_id']] = row['community_id']

        cid = row['community_id']
        if cid:
            if cid not in ctx:
                ctx[cid] = []
            ctx[cid].append(author['id'])

    # TODO: optimize
    titles = {}
    roles = {}
    for cid, account_ids in ctx.items():
        sql = "SELECT title FROM hive_communities WHERE id = :id"
        titles[cid] = await db.query_one(sql, id=cid)
        sql = """SELECT account_id, role_id, title
                   FROM hive_roles
                  WHERE community_id = :cid
                    AND account_id IN :ids"""
        roles[cid] = {}
        ret = await db.query_all(sql, cid=cid, ids=tuple(account_ids))
        for row in ret:
            name = author_ids[row['account_id']]
            roles[cid][name] = (row['role_id'], row['title'])

    for pid, post in posts_by_id.items():
        author = post['author']
        cid = post_cids[pid]
        if cid:
            post['community'] = post['category'] # TODO: True?
            post['community_title'] = titles[cid] or post['category']
            role = roles[cid][author] if author in roles[cid] else (0, '')
            post['author_role'] = ROLES[role[0]]
            post['author_title'] = role[1]
        else:
            post['stats']['gray'] = ('irredeemables' in post['blacklists']
                                     or len(post['blacklists']) >= 2)
        post['stats']['hide'] = 'irredeemables' in post['blacklists']


    sql = """SELECT id FROM hive_posts
              WHERE id IN :ids AND is_pinned = '1' AND is_deleted = '0'"""
    for pid in await db.query_col(sql, ids=tuple(ids)):
        if pid in posts_by_id:
            posts_by_id[pid]['stats']['is_pinned'] = True

    return posts_by_id

async def load_posts(db, ids, truncate_body=0):
    """Given an array of post ids, returns full objects in the same order."""
    if not ids:
        return []

    # posts are keyed by id so we can return output sorted by input order
    posts_by_id = await load_posts_keyed(db, ids, truncate_body=truncate_body)

    # in rare cases of cache inconsistency, recover and warn
    missed = set(ids) - posts_by_id.keys()
    if missed:
        log.info("get_posts do not exist in cache: %s", repr(missed))
        for _id in missed:
            ids.remove(_id)
            sql = ("SELECT id, author, permlink, depth, created_at, is_deleted "
                   "FROM hive_posts WHERE id = :id")
            post = await db.query_row(sql, id=_id)
            if not post['is_deleted']:
                # TODO: This should never happen. See #173 for analysis
                log.error("missing post: %s", dict(post))
            else:
                log.info("requested deleted post: %s", dict(post))

    return [posts_by_id[_id] for _id in ids]

async def _query_author_map(db, posts):
    """Given a list of posts, returns an author->reputation map."""
    if not posts: return {}
    names = tuple({post['author'] for post in posts})
    sql = "SELECT id, name, reputation FROM hive_accounts WHERE name IN :names"
    return {r['name']: r for r in await db.query_all(sql, names=names)}

def _condenser_profile_object(row):
    """Convert an internal account record into legacy-steemd style."""

    blacklists = Mutes.lists(row['name'], row['reputation'])

    return {
        'id': row['id'],
        'name': row['name'],
        'created': json_date(row['created_at']),
        'active': json_date(row['active_at']),
        'post_count': row['post_count'],
        'reputation': row['reputation'],
        'blacklists': blacklists,
        'stats': {
            'sp': int(row['vote_weight'] * 0.0005037),
            'rank': row['rank'],
            'following': row['following'],
            'followers': row['followers'],
        },
        'metadata': {
            'profile': {'name': row['display_name'],
                        'about': row['about'],
                        'website': row['website'],
                        'location': row['location'],
                        'cover_image': row['cover_image'],
                        'profile_image': row['profile_image'],
                       }}}

def _condenser_post_object(row, truncate_body=0):
    """Given a hive_posts row, create a legacy-style post object."""
    paid = row['is_paidout']

    # condenser#3424 mitigation
    if not row['category']:
        row['category'] = 'undefined'

    post = {}
    post['post_id'] = row['id']
    post['author'] = row['author']
    post['permlink'] = row['permlink']
    post['category'] = row['category']

    post['title'] = row['title']
    post['body'] = row['body'][0:truncate_body] if truncate_body else row['body']
    post['json_metadata'] = json.loads(row['json'])

    post['created'] = json_date(row['created_at'])
    post['updated'] = json_date(row['updated_at'])
    post['depth'] = row['depth']
    post['children'] = row['children']
    post['net_rshares'] = row['rshares']

    post['is_paidout'] = row['is_paidout']
    post['payout_at'] = json_date(row['payout_at'])
    post['payout'] = float(row['payout'])
    post['pending_payout_value'] = _amount(0 if paid else row['payout'])
    post['author_payout_value'] = _amount(row['payout'] if paid else 0)
    post['curator_payout_value'] = _amount(0)
    post['promoted'] = _amount(row['promoted'])

    post['replies'] = []
    post['active_votes'] = _hydrate_active_votes(row['votes'])
    post['author_reputation'] = row['author_rep']

    post['stats'] = {
        'hide': row['is_hidden'],
        'gray': row['is_grayed'],
        'total_votes': row['total_votes'],
        'flag_weight': row['flag_weight']} # TODO: down_weight


    #post['author_reputation'] = rep_to_raw(row['author_rep'])

    post['root_author'] = row['root_author']
    post['root_permlink'] = row['root_permlink']

    post['allow_replies'] = row['allow_replies']
    post['allow_votes'] = row['allow_votes']
    post['allow_curation_rewards'] = row['allow_curation_rewards']

    post['url'] = row['url']
    post['root_title'] = row['root_title']
    post['beneficiaries'] = row['beneficiaries']
    post['max_accepted_payout'] = row['max_accepted_payout']
    post['percent_steem_dollars'] = row['percent_steem_dollars']

    if paid:
        curator_payout = sbd_amount(row['curator_payout_value'])
        post['curator_payout_value'] = _amount(curator_payout)
        post['total_payout_value'] = _amount(row['payout'] - curator_payout)

    # not used by condenser, but may be useful
    # post['net_votes'] = post['total_votes'] - row['up_votes']

    # TODO: re-evaluate
    if row['depth'] > 0:
        post['parent_author'] = row['parent_author']
        post['parent_permlink'] = row['parent_permlink']
        post['title'] = 'RE: ' + row['root_title'] # PostSummary & comment context

    return post

def _amount(amount, asset='HBD'):
    """Return a steem-style amount string given a (numeric, asset-str)."""
    assert asset == 'HBD', 'unhandled asset %s' % asset
    return "%.3f HBD" % amount

def _hydrate_active_votes(vote_csv):
    """Convert minimal CSV representation into steemd-style object."""
    if not vote_csv: return []
    #return [line.split(',')[:2] for line in vote_csv.split("\n")]
    votes = []
    for line in vote_csv.split("\n"):
        voter, rshares, _, _ = line.split(',')
        votes.append(dict(voter=voter, rshares=rshares))
    return votes
