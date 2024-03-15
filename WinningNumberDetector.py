roulette_numbers: list[int] = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 26, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
n: int = len(roulette_numbers)


def detect_winning_number(zero_angle_deg: float, ball_angle_deg: float) -> int:
    diff = ball_angle_deg - zero_angle_deg
    single_slot_degrees = 360.0 / n
    ball_at = (diff + 360) / single_slot_degrees # - single_slot_degrees / 2
    ball_at_idx = round(ball_at) % n
    # print(ball_angle_deg, zero_angle_deg, diff, single_slot_degrees, ball_at, ball_at_idx, numbers[ball_at_idx])
    winning = roulette_numbers[ball_at_idx]
    return winning
