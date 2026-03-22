
def game_of_life_next_frame(grid: list[list[int]]) -> list[list[int]]:

    rows = len(grid)
    cols = len(grid[0])
    new_grid = [[0 for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            new_grid[i][j] = grid[i][j]
    return new_grid


def irrelevant_function():
    #just write harmonic series partial sum function
    def harmonic_series_partial_sum(n):
        if n <= 0:
            return 0
        else:
            return 1/n + harmonic_series_partial_sum(n-1)
    print(harmonic_series_partial_sum(10))
    print("this is an irrelevant function")
    return 0
    pass