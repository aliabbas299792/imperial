from bot_control.BotInterface import BotInterface, ControlBot


class PositionControlBot(ControlBot):
    def __init__(
        self, bot: BotInterface, base_move_dist: int = 800, turn_amount: int = 250
    ):
        super().__init__(bot)
        self.base_move_dist = base_move_dist
        self.turn_amount = turn_amount

    def _move(
        self, right_displacement: int, left_displacement: int
    ) -> "PositionControlBot":
        self.wait_for_movement_completion()

        curr_l = self.bot.get_left_position()
        curr_r = self.bot.get_right_position()
        self.bot.set_left_position(curr_l + left_displacement)
        self.bot.set_right_position(curr_r + right_displacement)
        return self

    def move_forward(self, distance=None) -> "PositionControlBot":
        if distance == None:
            distance = self.base_move_dist
        return self._move(distance, distance)

    def move_backward(self, distance=None) -> "PositionControlBot":
        if distance == None:
            distance = self.base_move_dist
        return self._move(-distance, -distance)

    def turn_left(self, amount=None) -> "PositionControlBot":
        if amount == None:
            amount = self.turn_amount
        return self._move(amount, -amount)

    def turn_right(self, amount=None) -> "PositionControlBot":
        if amount == None:
            amount = self.turn_amount
        return self._move(-amount, amount)
