steps = [
    [
        # "Up" SQL statement
        """
        ALTER TABLE favorites
        ADD CONSTRAINT unique_user_park_favorite
        UNIQUE (user_id, park_code);
        """,
        # "Down" SQL statement
        """
        ALTER TABLE favorites
        DROP CONSTRAINT unique_user_park_favorite;
        """
    ],
]
