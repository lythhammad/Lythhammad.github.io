from models.reviews import ReviewIn
from queries.pool import pool


class ReviewsQueries:
    @staticmethod
    def _row_to_dict(cursor, row):
        """
        Convert a single database row into a dictionary keyed by
        column name, using the cursor's description.

        This replaces the same for-loop that was previously repeated
        in every method that read rows from the reviews table.
        """
        return {col.name: value for col, value in zip(cursor.description, row)}

    def create_review(self, review: ReviewIn, user_id: int, username: str):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                params = [
                    review.comment,
                    user_id,
                    review.park_code,
                    username,
                    review.rating,
                ]
                cur.execute(
                    """
                    INSERT INTO reviews (
                        comment, user_id, park_code, username, rating)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, comment, user_id, park_code, username, rating
                    """,
                    params,
                )

                row = cur.fetchone()
                if row is None:
                    return None
                return self._row_to_dict(cur, row)

    def get_user_reviews(self, user_id: int):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, comment, user_id, park_code, rating
                    FROM reviews
                    WHERE user_id = %s
                    """,
                    [user_id],
                )
                return [
                    self._row_to_dict(cur, row) for row in cur.fetchall()
                ]

    def delete_review(self, user_id: int, id: int):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM reviews
                    WHERE id = %s AND user_id = %s
                    """,
                    [id, user_id],
                )
                if cur.rowcount > 0:
                    return "Deletion: Success"
                else:
                    return "Deletion: Failed"

    def get_all_reviews(self, park_code: str = None, sort_by: str = None):
        """
        Retrieve reviews, optionally filtered by park and sorted.

        sort_by accepts:
          - "rating": highest rating first
          - "newest": most recently created first (requires a
            created_at column; falls back to id if not present)
          - None: raw database order (previous default behavior)
        """
        query = """
            SELECT id, comment, user_id, park_code, username, rating
            FROM reviews
        """
        params = []

        if park_code is not None:
            query += " WHERE park_code = %s"
            params.append(park_code)

        if sort_by == "rating":
            query += " ORDER BY rating DESC"
        elif sort_by == "newest":
            query += " ORDER BY id DESC"

        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return [
                    self._row_to_dict(cur, row) for row in cur.fetchall()
                ]

    def get_average_rating_by_park(self, park_code: str):
        """
        Compute the average review rating for a given park.

        Returns a dict with park_code, average_rating (rounded to 2
        decimal places, or None if the park has no reviews yet), and
        review_count.
        """
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        park_code,
                        ROUND(AVG(rating)::numeric, 2) AS average_rating,
                        COUNT(*) AS review_count
                    FROM reviews
                    WHERE park_code = %s
                    GROUP BY park_code
                    """,
                    [park_code],
                )
                row = cur.fetchone()
                if row is None:
                    return {
                        "park_code": park_code,
                        "average_rating": None,
                        "review_count": 0,
                    }
                return self._row_to_dict(cur, row)
