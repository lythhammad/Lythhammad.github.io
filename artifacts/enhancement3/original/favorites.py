from models.favorites import FavoriteIn, FavoriteOut, Favorites
from queries.pool import pool


class FavoritesQueries():

    def create_favorite(
            self, favorites: FavoriteIn, user_id: int) -> Favorites:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO favorites
                        (user_id, park_code)
                    VALUES
                    (%s,%s)
                    RETURNING id;
                    """,
                    [
                        user_id,
                        favorites.park_code,
                    ]
                )
                id = cur.fetchone()[0]
                data = favorites.dict()
                return FavoriteOut(id=id, user_id=user_id, **data)

    def get_user_favorites(self, user_id: int):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, user_id, park_code
                    FROM favorites
                    WHERE user_id = %s
                    """,
                    [
                        user_id
                    ]
                )
                rows = cur.fetchall()
                favorites = []
                for row in rows:
                    id, user_id, park_code = row
                    favorite = FavoriteOut(
                        id=id, user_id=user_id, park_code=park_code)
                    favorites.append(favorite)
                return favorites

    def delete_favorite(self, user_id: int, id: int):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM favorites
                    WHERE id = %s AND user_id = %s
                    """,
                    [
                        id,
                        user_id
                    ]
                )
                if cur.rowcount > 0:
                    return "Deletion: Success"
                else:
                    return "Deletion: Failed"

    def get_all_favorites(self):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, user_id, park_code
                    FROM favorites
                    """
                )
                results = []
                for row in cur.fetchall():
                    favorite = {}
                    for i, col in enumerate(cur.description):
                        favorite[col.name] = row[i]
                    results.append(favorite)
                return results
