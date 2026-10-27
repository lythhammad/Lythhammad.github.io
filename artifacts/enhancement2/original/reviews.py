from models.reviews import ReviewIn
from queries.pool import pool


class ReviewsQueries():
    def create_review(self, review: ReviewIn, user_id: int, username: str):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                params = [
                    review.comment,
                    user_id,
                    review.park_code,
                    username,
                    review.rating
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

                record = None
                row = cur.fetchone()
                if row is not None:
                    record = {}
                    for i, col in enumerate(cur.description):
                        record[col.name] = row[i]

                return record

    def get_user_reviews(self, user_id: int):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, comment, user_id, park_code, rating
                    FROM reviews
                    WHERE user_id = %s
                    """,
                    [
                        user_id
                    ]
                )
                results = []
                for row in cur.fetchall():
                    review = {}
                    for i, col in enumerate(cur.description):
                        review[col.name] = row[i]
                    results.append(review)
                return results

    def delete_review(self, user_id: int, id: int):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM reviews
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

    def get_all_reviews(self):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, comment, user_id, park_code, username, rating
                    FROM reviews
                    """
                )
                results = []
                for row in cur.fetchall():
                    review = {}
                    for i, col in enumerate(cur.description):
                        review[col.name] = row[i]
                    results.append(review)
                return results
