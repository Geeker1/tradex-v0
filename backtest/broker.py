
class Broker:

    def __init__(self):
        self.initial_amount = 1000
        self.wins = 0
        self.losses = 0
        self.stale = 0
        self.trades = 0

        self.payout = 10
        self.loseout = 10

    def set_amount(self, amount):
        self.initial_amount = amount

    def update_stale(self):
        self.stale += 1

    def reduce_amount(self):
        self.initial_amount -= self.loseout
        self.losses += 1

    def increase_trades(self):
        self.trades += 1

    def increase_amount(self):
        self.wins += 1
        self.initial_amount += self.payout

    def get_stats(self):
        print(f"Wins == {self.wins}\nLosses == {self.losses}")
        print(f"Win percentage == {(self.wins/self.trades)*100}%")
        print(f"Loss percentage == {(self.losses/self.trades)*100}%")
        print(f"Stale == {self.stale}")
