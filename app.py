rows, cols = 10, 10
graph = [[0 for _ in range(cols)] for _ in range(rows)]

def bfs(start, end):
    queue = [[start]]  # Start with the start node
    visited = set()  # Keep track of visited nodes
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

    while queue:
        path = queue.pop(0)  # Get the first path in the queue
        x, y = path[-1]  # Get the last node in the path

        if (x, y) == end:
            return path  # Return the path if we reach the end

        if (x, y) not in visited:  # If the node has not been visited
            visited.add((x, y))  # Mark the node as visited
            for dx, dy in directions:  # Check all possible directions
                nx, ny = x + dx, y + dy  # Calculate the new node
                if 0 <= nx < rows and 0 <= ny < cols:  # Check if the new node is within the bounds
                    if (nx, ny) not in visited:  # Check if the new node is not visited
                        new_path = list(path) + [(nx, ny)]  # Add the new node to the path
                        queue.append(new_path)  # Add the new path to the queue

    return None  # Return None if no path is found

def visualize_path(path, start, end):
    # Create a grid for visualization
    visual_grid = [['[ ]' for _ in range(cols)] for _ in range(rows)]

    # Mark the start and end points
    sx, sy = start
    ex, ey = end
    visual_grid[sx][sy] = '[*]'
    visual_grid[ex][ey] = '[*]'

    # Mark the path taken, including the first step
    for (x, y) in path:
        visual_grid[x][y] = '[=]'

    # Print the visual grid
    for row in visual_grid:
        print(' '.join(row))

start_node = (0, 0)
end_node = (4, 8)

path_in = bfs(start_node, end_node)
if path_in:
    visualize_path(path_in, start_node, end_node)
else:
    print("No path found")