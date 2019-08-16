from collections import OrderedDict
import secrets


class BaseBroker:

    def __init__(self):
        self.wins = 0
        self.losses = 0
        self.buy = 0
        self.sell = 0
        self.trades = 0
        self.balance = 100
        self.orders = []
        self.completed = []

    def set_amount(self, amount):
        self.balance = amount

    def increase_trades(self):
        self.trades += 1

    def update_win(self):
        self.wins += 1

    def update_losses(self):
        self.losses += 1


class ForexBroker(BaseBroker):

    lot_size = 0.01  # Default lot size of 0.01$ per pip
    spread = lot_size * 22  # Default spread amount in USD
    takePip = 60
    stopPip = 20
    takeAmount = lot_size * takePip
    stopAmount = lot_size * stopPip
    pricePip = 0.0001

    def __init__(self):
        super().__init__()

    def reduce_amount(self):
        self.balance -= self.stopAmount
        self.update_losses()

    def increase_amount(self):
        self.balance += self.takeAmount
        self.update_win()

    def create_order(self, option, price, time):
        if option == "sell":
            takePrice = price - (self.takePip * self.pricePip)
            stopPrice = price + (self.stopPip * self.pricePip)
            self.sell += 1
        elif option == "buy":
            takePrice = price + (self.takePip * self.pricePip)
            stopPrice = price - (self.stopPip * self.pricePip)
            self.buy += 1

        order = OrderedDict(
            order_type=option,
            lot_size=self.lot_size,
            takePrice=takePrice,
            stopPrice=stopPrice,
            time=time,
            tradeID=secrets.token_hex(),
            done=False
        )
        self.orders.append(order)
        self.increase_trades()
        self.balance -= self.spread

    def verify_order(self, high, low, time):
        if isinstance(high, float) and isinstance(low, float):
            for order in self.orders:
                if order['done']:
                    continue
                if order['order_type'] == 'buy':
                    if order['takePrice'] <= high:
                        self.increase_amount()
                        self.completed.append((
                            order.get('order_type'),
                            'won', order.get('time'),
                            time))
                        order.update(done=True)
                    elif order['stopPrice'] >= low:
                        self.reduce_amount()
                        self.completed.append((
                            order.get('order_type'),
                            'lost', order.get('time'),
                            time))
                        order.update(done=True)

                elif order['order_type'] == 'sell':
                    if order['takePrice'] >= low:
                        self.increase_amount()
                        self.completed.append((
                            order.get('order_type'),
                            'won', order.get('time'),
                            time))
                        order.update(done=True)
                    elif order['stopPrice'] <= high:
                        self.reduce_amount()
                        self.completed.append((
                            order.get('order_type'),
                            'lost', order.get('time'),
                            time))
                        order.update(done=True)
            return
        raise TypeError("Values passed don't match")

    def history(self):
        print(f"### Wins == {self.wins} <===> Losses == {self.losses} ###")

        try:
            win_percent = (self.wins / self.trades) * 100
        except ZeroDivisionError:
            print("No win percentage")
        else:
            print(f"Win percentage == {win_percent}%")

        try:
            loss_percent = (self.losses / self.trades) * 100
        except ZeroDivisionError:
            print("No loss percentage")
        else:
            print(f"Loss percentage == {loss_percent}%")


class BinaryBroker(BaseBroker):

    def __init__(self):
        super().__init__()
        self.stale = 0
        self.payout = 10
        self.loseout = 10
        self.win_frames = OrderedDict(buy=[], sell=[])
        self.lose_frames = OrderedDict(buy=[], sell=[])

    def update_stale(self):
        self.stale += 1

    def reduce_amount(self):
        self.balance -= self.loseout
        self.update_losses()

    def increase_amount(self):
        self.balance += self.payout
        self.update_win()

    def create_order(self, option, price, time):
        order = OrderedDict(
            option=option,
            price=price,
            time=time,
            tradeID=secrets.token_hex(),
            done=False,
        )

        exec(f'self.{option} += 1')

        self.orders.append(order)
        self.trades += 1

    def verify_order(self, new_price, time, frame):
        for order in self.orders:
            diff = new_price - order.get('price')
            option = order.get('option')
            if order['done']:
                continue
            if option == 'buy':
                if diff > 0:
                    self.increase_amount()
                    self.completed.append(
                        (option, 'win', order.get('time'), time))
                    self.win_frames[option].append(frame)
                elif diff < 0:
                    self.reduce_amount()
                    self.completed.append(
                        (option, 'lose', order.get('time'), time))
                    self.lose_frames[option].append(frame)
                else:
                    self.update_stale(
                        (option, 'stale'))
                    self.completed.append(
                        (option, 'stale', order.get('time'), time))
                order.update(done=True)

            elif option == 'sell':
                if diff < 0:
                    self.increase_amount()
                    self.completed.append(
                        (option, 'win', order.get('time'), time))
                    self.win_frames[option].append(frame)
                elif diff > 0:
                    self.reduce_amount()
                    self.completed.append(
                        (option, 'lose', order.get('time'), time))
                    self.lose_frames[option].append(frame)
                else:
                    self.stale += 1
                    self.completed.append(
                        (option, 'stale', order.get('time'), time))
                order.update(done=True)

    def get_stats(self):
        print(f"Wins == {self.wins}\nLosses == {self.losses}")
        print(f"Stale == {self.stale}")

        try:
            win_percent = (self.wins / self.trades) * 100
        except ZeroDivisionError:
            print("No win percentage")
        else:
            print(f"Win percentage == {win_percent}%")

        try:
            loss_percent = (self.losses / self.trades) * 100
        except ZeroDivisionError:
            print("No loss percentage")
        else:
            print(f"Loss percentage == {loss_percent}%")
