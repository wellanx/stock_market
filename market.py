import math
import random

class Market:
    def __init__(self, db):
        self.db = db

    def get_stocks(self):
        self.db.cursor.execute("""
            SELECT * FROM stocks
        """)
        return self.db.cursor.fetchall()

    def update_market(self, player_instance):
        self.db.cursor.execute("""
            SELECT * FROM stocks
        """)
        rows = self.db.cursor.fetchall()
        
        dt = 1 / 252
        for ticker, current_price, drift, volatility in rows:
            z = random.gauss(0, 1)
            new_price = current_price * math.exp((drift - 0.5 * volatility**2) * dt + volatility * math.sqrt(dt) * z)
            
            self.db.cursor.execute("""
                UPDATE stocks SET current_price = ?
                WHERE ticker = ?
            """, (new_price, ticker))

            player_instance.refresh_portfolio_stock(new_price, ticker)

        self.db.conn.commit()