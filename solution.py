import itertools


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

assignments = []
digits = '123456789'
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
unitlist = ([cross(r, cols) for r in rows] +            # row_units
            [cross(rows, c) for c in cols] +            # col_units
            [cross(rs, cs)                              # square_units
                for rs in ('ABC', 'DEF', 'GHI')
                for cs in ('123', '456', '789')] +
            [                                           # diag_units
                [''.join(x) for x in zip(rows, cols)],
                [''.join(x) for x in zip(rows, cols[::-1])]])
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], []))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.

    Don't waste memory appending actions that don't actually change any values
    """

    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    for unit in unitlist:
        poss_twin_locs = [box for box in unit if len(values[box]) == 2]
        actual_twins = [(a, b)
                        for a, b in itertools.combinations(poss_twin_locs, 2)
                        if values[a] == values[b]]
        for twins in actual_twins:
            for box in unit:
                if box not in twins:
                    new_value = values[box]
                    for digit in values[twins[0]]:
                        new_value = new_value.replace(digit, '')
                    values = assign_value(values, box, new_value)
    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value,
            then the value will be '123456789'.
    """
    chars = [c if c in digits else digits for c in grid]
    assert len(chars) == 81
    return dict(zip(boxes, chars))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    return


def eliminate(values):
    solved = [k for k, v in values.items() if len(v) == 1]
    for box in solved:
        digit = values[box]
        for peer in peers[box]:
            values = assign_value(values, peer,
                                  values[peer].replace(digit, ''))
    return values


def only_choice(values):
    for unit in unitlist:
        for digit in digits:
            digit_locs = [box for box in boxes if digit in values[box]]
            if len(digit_locs) == 1:
                values = assign_value(values, digit_locs[0], digit)
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys()
                                    if len(values[box]) == 1])
        values = only_choice(naked_twins(eliminate(values)))
        solved_values_after = len([box for box in values.keys()
                                   if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    values = reduce_puzzle(values)
    if not values:
        return False
    if all(len(values[box]) == 1 for box in boxes):
        return values
    _, box = min((values[box], box) for box in boxes if len(values[box]) > 1)
    for value in values[box]:
        attempt = values.copy()
        attempt[box] = value
        attempt = search(attempt)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: ('2.............62....1....7...6..8...3...9'
                      '...7...6..4...4....8....52.............3')
    Returns:
        The dictionary representation of the final sudoku grid. False if no
        solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = ('2.............62....1....7...6..8...3...9'
                        '...7...6..4...4....8....52.............3')
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. '
              'Not a problem! It is not a requirement.')
