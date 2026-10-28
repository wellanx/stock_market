class Player:
    def __init__(self, db, player_id):
        self.db = db
        self.player_id = player_id

    def get_name(self):
        self.db.cursor.execute("""
            SELECT name FROM players
            WHERE id = ?
        """, (self.player_id,))
        row = self.db.cursor.fetchone()
        if row is None:
            return None
        return row[0]

    def create_profile(self, name):
        self.db.cursor.execute("""
            INSERT INTO players (id, name, balance)
            VALUES (?, ?, 10_000.00)
        """, (self.player_id, name))
        self.db.conn.commit()

    def buy_stock(self, ticker, order_size, current_day):
        if order_size <= 0:
            return False, 'Количество должно быть больше нуля'
        
        self.db.cursor.execute("""
            SELECT current_price FROM stocks WHERE ticker = ?
        """, (ticker,))
        rows = self.db.cursor.fetchone()

        if rows is None:
            return False, 'Такой акции не существует!'
        else:
            price = rows[0]
            cost = price * order_size

        self.db.cursor.execute("""
            SELECT balance FROM players
            WHERE id = ?
        """, (self.player_id,))
        rows = self.db.cursor.fetchone()
        balance = rows[0]
        
        if cost > balance:
            return False, f'Недостаточно средств. Вы пытаетесь купить {order_size} акций {ticker} по цене {cost:,.2f}. Ваш баланс {balance:,.2f}'
        else:
            balance -= cost
            avg = cost / order_size
            
            self.db.cursor.execute("""
                UPDATE players SET balance = ?
                WHERE id = ?
            """, (balance, self.player_id))
            
            self.db.cursor.execute("""
                INSERT INTO stock_portfolio (player_id, ticker, quantity, total_cost, avg_purc_price)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (player_id, ticker)
                DO UPDATE SET quantity = quantity + excluded.quantity, total_cost = total_cost + excluded.total_cost, avg_purc_price = (total_cost + excluded.total_cost) / (quantity + excluded.quantity)
            """, (self.player_id, ticker, order_size, cost, avg))

            self.db.cursor.execute("""
                INSERT INTO transaction_history (transaction_type, ticker, quantity, price, total_amount, date)
                VALUES ('BUY', ?, ?, ?, ?, ?)
            """, (ticker, order_size, price, cost, current_day))
            
            self.db.conn.commit()
            
            return True, f'Успех!\nКуплено: {ticker} в размере {order_size}.\nОстаток средств: {balance:,.2f}'

    def refresh_portfolio_stock(self, new_price, ticker):
            
            self.db.cursor.execute("""
                SELECT avg_purc_price FROM stock_portfolio
                WHERE player_id = ? AND ticker = ?
            """, (self.player_id, ticker))
            avg_price = self.db.cursor.fetchone()

            if avg_price is None:
                return
            
            perc_change = ((new_price - avg_price[0]) / avg_price[0]) * 100
            self.db.cursor.execute("""
                UPDATE stock_portfolio SET current_price = ?, percentage_change = ?
                WHERE player_id = ? AND ticker = ?
            """, (new_price, perc_change, self.player_id, ticker))

    def check_balance(self):
        self.db.cursor.execute("""
            SELECT balance FROM players
            WHERE id = ?
        """, (self.player_id,))
        balance = self.db.cursor.fetchone()
        return f'Баланс: ${balance[0]:.2f}'

    def show_portfolio(self):
        self.db.cursor.execute("""
            SELECT * FROM stock_portfolio
            WHERE player_id = ?
        """, (self.player_id,))
        return self.db.cursor.fetchall()

    def sell_stock(self, ticker, order_size, current_day):
        if order_size <= 0:
            return False, 'Количество должно быть больше нуля!'
        self.db.cursor.execute("""
            SELECT quantity FROM stock_portfolio
            WHERE player_id = ? AND ticker = ?
        """, (self.player_id, ticker))
        row = self.db.cursor.fetchone()

        if row is None:
            return False, 'Не нашлость такой акции в вашем портфеле!'

        quantity = row[0]
        if order_size > quantity:
            return False, 'Вы пытаетесь продать больше акций, чем есть у вас есть в портфолио!'

        self.db.cursor.execute("""
            SELECT current_price FROM stocks
            WHERE ticker = ?
        """, (ticker,))
        row = self.db.cursor.fetchone()
        current_price = row[0]

        sale_amount = current_price * order_size
        quantity -= order_size
        if quantity == 0:
            self.db.cursor.execute("""
                DELETE FROM stock_portfolio
                WHERE player_id = ? AND ticker = ?
            """, (self.player_id, ticker))
        else:
            self.db.cursor.execute("""
                UPDATE stock_portfolio SET quantity = ?
                WHERE player_id = ? AND ticker = ?
            """, (quantity, self.player_id, ticker))
            self.db.cursor.execute("""
                SELECT avg_purc_price, total_cost FROM stock_portfolio
                WHERE player_id = ? AND ticker = ?
            """, (self.player_id, ticker))
            row = self.db.cursor.fetchone()
            avg_purc_price, total_cost = row
            
            total_cost -= avg_purc_price * order_size
            self.db.cursor.execute("""
                UPDATE stock_portfolio SET total_cost = ?
                WHERE player_id = ? AND ticker = ?
            """, (total_cost, self.player_id, ticker))

        self.db.cursor.execute("""
            SELECT balance FROM players
            WHERE id = ?
        """, (self.player_id,))
        row = self.db.cursor.fetchone()
        balance = row[0]

        balance += sale_amount
        self.db.cursor.execute("""
            UPDATE players SET balance = ?
            WHERE id = ?
        """, (balance, self.player_id))

        self.db.cursor.execute("""
            INSERT INTO transaction_history (transaction_type, ticker, quantity, price, total_amount, date)
            VALUES ('SELL', ?, ?, ?, ?, ?)
        """, (ticker, order_size, current_price, sale_amount, current_day))

        self.db.conn.commit()

        return True, f'Успешно! Продано {ticker} в размере {order_size}'

    def show_transaction_history(self):
        self.db.cursor.execute("""
            SELECT * FROM transaction_history
        """)
        rows = self.db.cursor.fetchall()
        return rows
