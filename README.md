# Kivy-3D-Rubik's-Cube

This project demonstrates how to create a 3D Rubik's cube using the Kivy framework in Python. Kivy is an open-source Python library for developing multitouch applications. This example showcases basic 3D rendering and interaction without using OpenGL or shaders.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/MAT06mat/Kivy-3D-Rubik-s-Cube.git
    ```

2. Navigate to the project directory:
    ```sh
    cd Kivy-3D-Rubik-s-Cube
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To start the application, run the `main.py` file:
```sh
python main.py
```

You can also import the `RubiksCube` class with:
```py
from main import RubiksCube
```

## Features

- 3D visualization of a Rubik's cube
- Interactive manipulation of the cube
- Reset and scramble functionalities

## Documentation

### Class `RubiksCube`

The `RubiksCube` class represents a 3D Rubik's cube and provides methods to manipulate it.

#### Variables

- `angle`: List of angles for rotation around the x, y, and z axes.
- `scale`: Scale factor for the size of the cube.
- `border`: Width of the border lines around each face.
- `allow_rotation`: Boolean to allow or disallow rotation of the cube.
- `max_y_rotation`: Boolean to limit the maximum rotation around the y-axis.
- `background_color`: Background color of the widget.
- `border_color`: Color of the border lines around each face.
- `frame_rate`: Frame rate of updating the cube.
- `faces_colors`: Color of each face.

#### Methods

- `from_string(self, patternstring: str) -> bool`: Constructs a cube from a string.
- `to_string(self, kociemba=False) -> str`: Returns the string representation of the cube.
- `turn(self, move: str) -> None`: Rotates a specified face of the cube using Rubik's Cube notation.
  - `move`: The move to perform (e.g., 'F', 'B', 'L', 'R', 'U', 'D').
- `is_solve(self) -> bool`: Returns `True` if the cube is solved.
- `solve(self, patternstring: str | None = None, max_depth: int = 24) -> str`: Solves the cube and returns the solution.
- `random(self, nb: int = random.randint(20, 30)) -> None`: Scrambles the cube randomly.

## License

This project is licensed under the MIT License.
