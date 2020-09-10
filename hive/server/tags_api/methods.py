from hive.server.common.helpers import (
    return_error_info,
    valid_account,
    valid_permlink)


@return_error_info
async def get_active_votes(context, author: str, permlink: str):
    """ Returns all votes for the given post. """
    valid_account(author)
    valid_permlink(permlink)
    db = context['db']
    sql = """
        SELECT 
            hv.voter,
            hv.author,
            hv.permlink,
            hv.weight,
            hv.rshares,
            hv.percent,
            hv.last_update,
            hv.num_changes
        FROM
            hive_votes_view hv
        WHERE hv.author = :author AND hv.permlink = :permlink
    """
    ret = []
    rows = await db.query_all(sql, author=author, permlink=permlink)
    for row in rows:
        ret.append(dict(voter=row.voter, author=row.author, permlink=row.permlink,
                        weight=row.weight, rshares=row.rshares, vote_percent=row.percent,
                        last_update=str(row.last_update), num_changes=row.num_changes))
    return ret

@return_error_info
async def get_tags_used_by_author(context, author: str):
    """ Returns a list of tags used by an author. """
    raise NotImplementedError()

@return_error_info
async def get_discussions_by_active(context, tag: str, limit: int, filter_tags: list,
                                    select_authors: list, select_tags: list, truncate_body: int):
    """ Returns a list of discussions based on active. """
    raise NotImplementedError()

@return_error_info
async def get_discussions_by_cashout(context, tag: str, limit: int, filter_tags: list,
                                     select_authors: list, select_tags: list, truncate_body: int):
    """ Returns a list of discussions by cashout. """
    raise NotImplementedError()

@return_error_info
async def get_discussions_by_votes(context, tag: str, limit: int, filter_tags: list,
                                   select_authors: list, select_tags: list, truncate_body: int):
    """ Returns a list of discussions by votes. """
    raise NotImplementedError()

@return_error_info
async def get_discussions_by_children(context, tag: str, limit: int, filter_tags: list,
                                      select_authors: list, select_tags: list, truncate_body: int):
    """ Returns a list of discussions by children. """
    raise NotImplementedError()
