class GameSession:
    def __init__(self, db):
        self.db = db

    def current_day(self):
            self.db.cursor.execute("""
                SELECT current_day FROM game_state
                WHERE id = 1
            """)
            row = self.db.cursor.fetchone()
            return row[0]

    def advance_day(self, market_instance, player_instance):
        self.db.cursor.execute("""
            UPDATE game_state SET current_day = current_day + 1
            WHERE id = 1
        """)
        market_instance.update_market(player_instance)
        self.db.conn.commit()
        