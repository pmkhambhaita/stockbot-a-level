class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]

class PathFinder:
    def __init__(self, grid):
        self.grid = grid
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

    def bfs(self, start, end):
        queue = [[start]]  # Start with the start node
        visited = set()  # Keep track of visited nodes

        while queue:
            path = queue.pop(0)  # Get the first path in the queue
            x, y = path[-1]  # Get the last node in the path

            if (x, y) == end:
                return path  # Return the path if we reach the end

            if (x, y) not in visited:  # If the node has not been visited
                visited.add((x, y))  # Mark the node as visited
                for dx, dy in self.directions:  # Check all possible directions
                    nx, ny = x + dx, y + dy  # Calculate the new node
                    if 0 <= nx < self.grid.rows and 0 <= ny < self.grid.cols:  # Check if the new node is within bounds
                        if (nx, ny) not in visited:  # Check if the new node is not visited
                            new_path = list(path) + [(nx, ny)]  # Add the new node to the path
                            queue.append(new_path)  # Add the new path to the queue

        return None  # Return None if no path is found

    def find_path_through_points(self, start, points, end):
        full_path = []
        current_start = start

        for point in points:
            path_segment = self.bfs(current_start, point)
            if path_segment:
                full_path.extend(path_segment[:-1])  # Exclude the last point to avoid duplication
                current_start = point
            else:
                return None  # Return None if any segment is not found

        final_segment = self.bfs(current_start, end)
        if final_segment:
            full_path.extend(final_segment)
        else:
            return None

        return full_path

class PathVisualiser:
    def __init__(self, grid):
        self.grid = grid

    def visualise_path(self, path, start, end, points=[]):
        # Create a grid for visualisation
        visual_grid = [['[ ]' for _ in range(self.grid.cols)] for _ in range(self.grid.rows)]

        # Mark the path taken
        for (x, y) in path:
            visual_grid[x][y] = '[=]'

        # Mark all points (start, end, and intermediate) with *
        sx, sy = start
        ex, ey = end
        visual_grid[sx][sy] = '[*]'
        visual_grid[ex][ey] = '[*]'
        for x, y in points:
            visual_grid[x][y] = '[*]'

        # Print the visual grid
        for row in visual_grid:
            print(' '.join(row))

# Example usage
rows, cols = 10, 10
grid = Grid(rows, cols)
path_finder = PathFinder(grid)
path_visualiser = PathVisualiser(grid)

start_node = (0, 0)
end_node = (rows - 1, cols - 1)
intermediate_points = [(2, 2), (5, 5), (7, 7)]  # Example intermediate points

# Update the example usage
path_in = path_finder.find_path_through_points(start_node, intermediate_points, end_node)
if path_in:
    path_visualiser.visualise_path(path_in, start_node, end_node, intermediate_points)
else:
    print("No path found")