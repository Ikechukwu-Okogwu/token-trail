

def game_of_life_next_frame(grid: list[list[int]]) -> list[list[int]]:

    rows_num = len(grid)
    cols_num = len(grid[0])
    new_grid = [[0 for _ in range(cols_num)] for _ in range(rows_num)]

    for i in range(rows_num):
        for j in range(cols_num):
            new_grid[i][j] = grid[i][j]
    return new_grid

def unrelated_function():
    #just write fibonacci function
    def fibonacci(n):
        if n <= 0:
            return 0
        elif n == 1:
            return 1
        else:
            return fibonacci(n-1) + fibonacci(n-2)
    print(fibonacci(10))
    print("this is an unrelated function")
    return 0
    pass
