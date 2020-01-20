from link_downloader.models import database, links


async def get_links_for_user(user_id: int):
    query = links.select(links.c.user_id == user_id)
    return await database.fetch_all(query)
