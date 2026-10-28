import logging

from psycopg.errors import UniqueViolation

from models.favorites import FavoriteIn, FavoriteOut, Favorites
from queries.pool import pool

logger = logging.getLogger(__name__)


class DuplicateFavoriteError(Exception):
    """Raised when a user tries to favorite a park they've already favorited."""
    pass


class FavoritesQueries:

    def create_favorite(
        self, favorites: FavoriteIn, user_id: int
    ) -> Favorites:
        try:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO favorites
                            (user_id, park_code)
                        VALUES
                        (%s, %s)
                        RETURNING id;
                        """,
                        [
                            user_id,
                            favorites.park_code,
                        ],
                    )
                    id = cur.fetchone()[0]
        except UniqueViolation:
            # Relies on the unique_user_park_favorite constraint added
            # in migration 003.
            logger.info(
                "Duplicate favorite attempt: user_id=%s park_code=%s",
                user_id,
                favorites.park_code,
            )
            raise DuplicateFavoriteError(
                "This park is already in your favorites."
            )
        except Exception:
            logger.exception(
                "Unexpected error creating favorite for user_id=%s", user_id
            )
            raise

        data = favorites.dict()
        return FavoriteOut(id=id, user_id=user_id, **data)

    def get_user_favorites(self, user_id: int):
        try:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, user_id, park_code
                        FROM favorites
                        WHERE user_id = %s
                        """,
                        [user_id],
                    )
                    rows = cur.fetchall()
        except Exception:
            logger.exception(
                "Unexpected error retrieving favorites for user_id=%s",
                user_id,
            )
            raise

        favorites = []
        for row in rows:
            id, user_id, park_code = row
            favorite = FavoriteOut(id=id, user_id=user_id, park_code=park_code)
            favorites.append(favorite)
        return favorites

    def delete_favorite(self, user_id: int, id: int):
        try:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        DELETE FROM favorites
                        WHERE id = %s AND user_id = %s
                        """,
                        [id, user_id],
                    )
                    deleted = cur.rowcount > 0
        except Exception:
            logger.exception(
                "Unexpected error deleting favorite id=%s for user_id=%s",
                id,
                user_id,
            )
            raise

        return "Deletion: Success" if deleted else "Deletion: Failed"

    def get_all_favorites(self, limit: int = 50, offset: int = 0):
        """
        Retrieve favorites with pagination.

        limit caps how many rows come back at once (default 50, so a
        growing table doesn't pull every row into memory), and offset
        skips that many rows, so callers can page through results.
        """
        try:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, user_id, park_code
                        FROM favorites
                        ORDER BY id
                        LIMIT %s OFFSET %s
                        """,
                        [limit, offset],
                    )
                    rows = cur.fetchall()
                    results = []
                    for row in rows:
                        favorite = {}
                        for i, col in enumerate(cur.description):
                            favorite[col.name] = row[i]
                        results.append(favorite)
                    return results
        except Exception:
            logger.exception("Unexpected error retrieving all favorites.")
            raise
