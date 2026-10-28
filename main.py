import market
import player
import game
import db

market_instance = market.Market(db)
player_instance = player.Player(db, 1)
game_instance = game.GameSession(db)

def format_get_stocks(rows):
    prices = [f'{p:,.2f}' for _, p, _, _ in rows]
    name_width = max(len('Акция'), max(len(n) for n, _, _, _ in rows))
    price_width = max(len('Цена'), max(len(p) for p in prices))
    drift_width = max(len('Дрифт'), max(len(str(d)) for _, _, d, _ in rows))
    volatility_width = max(len('Волатильность'), max(len(str(v)) for _, _, _, v in rows))

    gap = ' ' * 4
    lines = [
        f"{'Акция':<{name_width}}{gap}"
        f"{'Цена':<{price_width}}{gap}"
        f"{'Дрифт':>{drift_width}}{gap}"
        f"{'Волатильность':>{volatility_width}}",
        '-' * 64
    ]

    for (ticker, _, drift, volatility), price in zip(rows, prices):
        lines.append(
            f'{ticker:<{name_width}}{gap}'
            f'{price:<{price_width}}{gap}'
            f'{drift:<{drift_width}}{gap}'
            f'{volatility:<{volatility_width}}{gap}'
            )
        
    lines.append(f"{'-' * 64}")
    return '\n'.join(lines)

def format_show_portfolio(rows):
    if not rows:
        return None
    
    stock = [s for _, s, _, _, _, _, _ in rows]
    quantity = [f'{q}' for _, _, q, _, _, _, _ in rows]
    total_cost = [float(f'{t:.2f}') for _, _, _, t, _, _, _ in rows]
    avg_price = [float(f'{a:.2f}') for _, _, _, _, a, _, _ in rows]
    current_price = [float(f'{c:.2f}') for _, _, _, _, _, c, _ in rows]
    percentage_change = [float(f'{pc:.2f}') for _, _, _, _, _, _, pc in rows]
    
    name_width = max(len('Акция'), max(len(s) for s in stock))
    quantity_width = max(len('Количество'), max(len(q) for q in quantity))
    total_width = max(len('Вложено'), max(len(str(q)) for q in total_cost))
    avg_width = max(len('Средняя цена'), max(len(str(q)) for q in avg_price))
    current_width = max(len('Текущая цена'), max(len(str(q)) for q in current_price))
    percentage_width = max(len('Изменение'), max(len(str(q)) for q in percentage_change))

    gap = ' ' * 4
    lines = [
        f"{'Акция':<{name_width}}{gap} "
        f"{'Количество':<{quantity_width}}{gap} "
        f"{'Вложено':<{total_width}}{gap} " 
        f"{'Средняя цена':<{avg_width}}{gap} " 
        f"{'Текущая цена':<{current_width}}{gap} " 
        f"{'Изменение':<{percentage_width}} ",
        '-' * 88
    ]

    for ticker, qu, total, avg, current, perc in zip(stock, quantity, total_cost, avg_price, current_price, percentage_change):
        if perc >= 0:
            lines.append(
                f'{ticker:<{name_width}}{gap} '
                f'{qu:<{quantity_width}}{gap} '
                f'{total:<{total_width}}{gap} '
                f'{avg:<{avg_width}}{gap} '
                f'{current:<{current_width}}{gap} '
                f'{perc:+.{2}f}%'
            )
        elif perc < 0:
            lines.append(
                f'{ticker:<{name_width}}{gap} '
                f'{qu:<{quantity_width}}{gap} '
                f'{total:<{total_width}}{gap} '
                f'{avg:<{avg_width}}{gap} '
                f'{current:<{current_width}}{gap} '
                f'{perc:-.{2}f}%'
            )
    
    lines.append(f"{'-' * 88}")
    return '\n'.join(lines)

def format_transaction_history(rows):
    if not rows:
        return None

    transaction_type = [t for t, _, _, _, _, _ in rows]
    ticker = [s for _, s, _, _, _, _ in rows]
    quantity = [str(q) for _, _, q, _, _, _ in rows]
    price = [f'{p:,.2f}' for _, _, _, p, _, _ in rows]
    total_amount = [f'{t:,.2f}' for _, _, _, _, t, _ in rows]
    date = [str(d) for _, _, _, _, _, d in rows]

    type_width = max(len('Тип операции'), max(len(t) for t in transaction_type))
    ticker_width = max(len('Акция'), max(len(s) for s in ticker))
    quantity_width = max(len('Количество'), max(len(q) for q in quantity))
    price_width = max(len('Цена'), max(len(p) for p in price))
    total_width = max(len('Сумма'), max(len(t) for t in total_amount))
    date_width = max(len('Дата'), max(len(d) for d in date))

    gap = ' ' * 4
    lines = [
        f"{'Тип операции':<{type_width}}{gap}"
        f"{'Акция':<{ticker_width}}{gap}"
        f"{'Количество':>{quantity_width}}{gap}"
        f"{'Цена':>{price_width}}{gap}"
        f"{'Сумма':>{total_width}}{gap}"
        f"{'Дата':<{date_width}}",
        '-' * 100
    ]

    for t, s, q, pr, total, d in zip(
        transaction_type, ticker, quantity, price, total_amount, date
    ):
        lines.append(
            f'{t:<{type_width}}{gap}'
            f'{s:<{ticker_width}}{gap}'
            f'{q:>{quantity_width}}{gap}'
            f'{pr:>{price_width}}{gap}'
            f'{total:>{total_width}}{gap}'
            f'{d:<{date_width}}'
        )

    lines.append('-' * 100)
    return '\n'.join(lines)

name = player_instance.get_name()

if name is None:
    name = input('Введите имя: ')
    player_instance.create_profile(name)
print('-' * 64)
print(f'Привет, {name}!')
print('-' * 64)

while True:
    print(f'Текущий день: {game_instance.current_day()}')
    print(player_instance.check_balance())
    print('-' * 64)

    print('Выберите действие:\n'
          '1. Купить акции\n'
          '2. Показать портфолио\n'
          '3. Посмотреть котировки\n'
          '4. Продать акции\n'
          '5. Пропустить день\n'
          '6. Посмотреть историю транзакций\n'
          '0. Выход из игры')
    choice = input('Ввод: ').lower()

    if choice == '0' or choice == 'выход из игры':
        print('-' * 64)
        print('До встречи!!!\n')
        break

    elif choice == '1' or choice == 'купить акции':
        print('-' * 64)
        print(format_get_stocks(market_instance.get_stocks()))
        print(player_instance.check_balance())
        while True:
            ticker = input('Введите название акции (для отмены введите 0): ').upper()

            if ticker == '0':
                print('-' * 64)
                break

            try:
                order_size = int(input('Введите желаемое количество (для отмены введите 0): '))
            except ValueError:
                print('Введите число!')
                continue
            else:
                if order_size == 0:
                    print('-' * 64)
                    break
            
            success, message = player_instance.buy_stock(ticker, order_size, game_instance.current_day())
            print(message)

            if success:
                game_instance.advance_day(market_instance, player_instance)
                back = input('\nВведите что угодно, чтобы вернуться назад\nВвод: ')
                print('-' * 64)
                break
            else:
                print('-' * 64) 
                continue
    
    elif choice == '2' or choice == 'показать портфолио':
        print('-' * 88)
        
        portfolio_view = format_show_portfolio(player_instance.show_portfolio())
        if portfolio_view is None:
            print('Пусто!')
            back = input('\nВведите что угодно, чтобы вернуться назад\nВвод: ')
            print('-' * 64)
        else:
            print(portfolio_view)
            back = input('\nВведите что угодно, чтобы вернуться назад\nВвод: ')
            print('-' * 88)

    elif choice == '3' or choice == 'посмотреть котировки':
        print('-' * 64)
        print(format_get_stocks(market_instance.get_stocks()))

        back = input('\nВведите что угодно, чтобы вернуться назад\nВвод: ')
        print('-' * 64)

    elif choice == '4' or choice == 'продать акции':
        portfolio_view = format_show_portfolio(player_instance.show_portfolio())

        while True:
            if portfolio_view is None:
                print('-' * 64)
                print('Пусто!')
                back = input('\nВведите что угодно, чтобы вернуться назад\nВвод: ')
                print('-' * 64)
                break

            print(portfolio_view)
            
            ticker = input('Выберите акцию из вашего портфеля, которую вы хотите продать (введите 0 для отмены): ').upper()

            if ticker == '0':
                break

            try:    
                order_size = int(input('Введите количество (введите 0 для отмены): '))
            except ValueError:
                print('Введите число!')
                continue
            else:
                if order_size == 0:
                    print('-' * 64)
                    break

            success, message = player_instance.sell_stock(ticker, order_size, game_instance.current_day())
            print(message)

            if success:
                game_instance.advance_day(market_instance, player_instance)
                back = input('\nВведите что угодно, чтобы вернуться назад\nВвод: ')
                print('-' * 64)
                break
            else:
                print('-' * 64) 
                continue

    elif choice == '5' or choice == 'пропустить день':
        print('-' * 64)
        confirmation = input('Вы уверены? Введите 0 для отмены: ')
        if confirmation == '0':
            print('-' * 64)
            continue
        else:
            game_instance.advance_day(market_instance, player_instance)
            print('Вы пропустили ход!\n')
            print('-' * 64)

    elif choice == '6' or choice == 'посмотреть историю транзакций':
        transactions = format_transaction_history(player_instance.show_transaction_history())

        if transactions is None:
            print('-' * 64)
            print('В истории пусто(')
            back = input('\nВведите что угодно, чтобы вернуться назад\nВвод: ')
            print('-' * 64)
        else:
            print(transactions)
            back = input('\nВведите что угодно, чтобы вернуться назад\nВвод: ')
            print('-' * 64)
    
    else:
        print('Выберите из предложенных действий!')
        print('-' * 64)

