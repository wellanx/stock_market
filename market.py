import math
import random
import sqlite3
import db

def get_stocks():
    db.cursor.execute("""
        SELECT * FROM stocks
    """)
    return db.cursor.fetchall()

def buy_stock(ticker, order_size):
    if order_size <= 0:
        return False, 'Количество должно быть больше нуля'
    db.cursor.execute("""
        SELECT current_price FROM stocks WHERE ticker = ?
    """, (ticker,))
    rows = db.cursor.fetchone()

    if rows is None:
        return False, 'Такой акции не существует!'
    else:
        price = rows[0]
        cost = price * order_size

    db.cursor.execute("""
        SELECT balance FROM player
    """)
    rows = db.cursor.fetchone()
    balance = rows[0]
    if cost > balance:
        return False, f'Недостаточно средств. Вы пытаетесь купить {order_size} акций {ticker} по цене {cost:,.2f}. Ваш баланс {balance:,.2f}'
    else:
        balance -= cost
        avg = cost / order_size
        db.cursor.execute("""
            UPDATE player SET balance = ?
        """, (balance,))
        db.cursor.execute("""
            INSERT INTO stock_portfolio (ticker, quantity, total_cost, avg_purc_price)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (ticker)
            DO UPDATE SET quantity = quantity + excluded.quantity, total_cost = total_cost + excluded.total_cost, avg_purc_price = (total_cost + excluded.total_cost) / (quantity + excluded.quantity)
        """, (ticker, order_size, cost, avg))
        db.conn.commit()
        return True, f'Успех!\nКуплено: {ticker} в размере {order_size}.\nОстаток средств: {balance:,.2f}'

def update_market():
    db.cursor.execute("""
        SELECT * FROM stocks
    """)
    rows = db.cursor.fetchall()
    
    dt = 1 / 252
    for ticker, current_price, drift, volatility in rows:
        z = random.gauss(0, 1)
        new_price = current_price * math.exp((drift - 0.5 * volatility**2) * dt + volatility * math.sqrt(dt) * z)
        db.cursor.execute("""
            UPDATE stocks SET current_price = ?
            WHERE ticker = ?
        """, (new_price, ticker))
        db.cursor.execute("""
            SELECT avg_purc_price FROM stock_portfolio
            WHERE ticker = ?
        """, (ticker,))
        avg_price = db.cursor.fetchone()
        if avg_price is None:
            continue
        else:
            perc_change = ((new_price - avg_price[0]) / avg_price[0]) * 100
        db.cursor.execute("""
            UPDATE stock_portfolio SET current_price = ?, percentage_change = ?
            WHERE ticker = ?
        """, (new_price, perc_change, ticker))
    db.conn.commit()


def check_balance():
    db.cursor.execute("""
        SELECT balance FROM player
    """)
    balance = db.cursor.fetchone()
    return f'Баланс: {balance[0]:.2f}'

def show_portfolio():
    db.cursor.execute("""
        SELECT * FROM stock_portfolio
    """)
    return db.cursor.fetchall()

def sell_stock(stock):
    pass