import market

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
        return 'Вы ничего не покупали!'
    
    stock = [s for s, _, _, _, _, _ in rows]
    quantity = [f'{q}' for _, q, _, _, _, _ in rows]
    total_cost = [float(f'{t:.2f}') for _, _, t, _, _, _ in rows]
    avg_price = [float(f'{a:.2f}') for _, _, _, a, _, _ in rows]
    current_price = [float(f'{c:.2f}') for _, _, _, _, c, _ in rows]
    percentage_change = [float(f'{pc:.2f}') for _, _, _, _, _, pc in rows]
    
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

while True:
    print('Выберите действие:\n'
          '1. Купить акции\n'
          '2. Проверить баланс\n'
          '3. Показать портфолио\n'
          '4. Посмотреть котировки\n'
          '5. Продать акции\n'
          '0. Выход из игры')
    choice = input('Ввод: ').lower()

    if choice == '0' or choice == 'выход из игры':
        print('-' * 64)
        print('До встречи!!!\n')
        break

    elif choice == '1' or choice == 'купить акции':
        print('-' * 64)
        print(format_get_stocks(market.get_stocks()))
            
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
            
            success, message = market.buy_stock(ticker, order_size)
            print(message)

            if success:
                market.update_market()
                back = input('\nВведите что угодно, чтобы вернуться назад\nВвод: ')
                print('-' * 64)
                break
            else:
                print('-' * 64) 
                continue
    
    elif choice == '2' or choice == 'проверить баланс':
        print('-' * 64)
        print(f'{market.check_balance()}$')

        back = input('\nВведите что угодно, чтобы вернуться назад\nВвод: ')
        print('-' * 64)
    
    elif choice == '3' or choice == 'показать портфолио':
        print('-' * 88)
        print(format_show_portfolio(market.show_portfolio()))

        back = input('\nВведите что угодно, чтобы вернуться назад\nВвод: ')
        print('-' * 88)

    elif choice == '4' or choice == 'посмотреть котировки':
        print('-' * 64)
        print(format_get_stocks(market.get_stocks()))

        back = input('\nВведите что угодно, чтобы вернуться назад\nВвод: ')
        print('-' * 64)

    elif choice == '5' or choice == 'продать акции':
        print(format_show_portfolio(market.show_portfolio()))
        while True: 
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

            success, message = market.sell_stock(ticker, order_size)
            print(message)

            if success:
                market.update_market()
                back = input('\nВведите что угодно, чтобы вернуться назад\nВвод: ')
                print('-' * 64)
                break
            else:
                print('-' * 64) 
                continue
            
    
    else:
        print('Выберите из предложенных действий!')
        print('-' * 64)

