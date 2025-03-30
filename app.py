rows, cols = 10, 10
graph = [[0 for _ in range(cols)] for _ in range(rows)]

def bfs(graph_in, start, end):
    queue = [[start]] # Start with the start node
    visited = set() # Keep track of visited nodes
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

    while queue:
        path = queue.pop(0) # Get the first path in the queue
        x, y = path[-1] # Get the last node in the path

        if (x, y) == end:
            return path # Return the path if we reach the end

        if (x, y) not in visited: # If the node has not been visited
            visited.add((x, y))  # Mark the node as visited
            for dx, dy in directions:  # Check all possible directions
                nx, ny = x + dx, y + dy  # Calculate the new node
                if 0 <= nx < rows and 0 <= ny < cols:  # Check if the new node is within the bounds
                    if (nx, ny) not in visited and graph_in[nx][ny] == 0:  # Check if the new node is not visited
                        new_path = list(path) + [(nx, ny)]  # Add the new node to the path
                        queue.append(new_path) # Add the new path to the queue

    return None  # Return None if no path is found


start_node = (0, 0)
end_node = (4, 8)

path_in = bfs(graph, start_node, end_node)
print(path_in)
