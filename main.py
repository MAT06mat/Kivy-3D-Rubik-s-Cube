from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Mesh, Rectangle
from kivy.properties import (
    ListProperty,
    NumericProperty,
    BooleanProperty,
    ColorProperty,
)
from kivy.input.motionevent import MotionEvent
from kivy.clock import Clock
from kivy.core.window import Window
import numpy as np
from math import cos, sin, pi

from cube import FACE_ORDER, Cube


class Cubie:
    def __init__(self, parent, r_pos: list[int]):
        self.parent: RubiksCube = parent
        self.r_pos = r_pos  # Relative pos
        # Define the 8 points of the cube
        self.points = [
            np.matrix([-1, -1, 1]),
            np.matrix([1, -1, 1]),
            np.matrix([1, 1, 1]),
            np.matrix([-1, 1, 1]),
            np.matrix([-1, -1, -1]),
            np.matrix([1, -1, -1]),
            np.matrix([1, 1, -1]),
            np.matrix([-1, 1, -1]),
        ]
        # Define the projection matrix
        self.projection_matrix = np.matrix([[1, 0, 0], [0, 1, 0]])
        self.projected_points = [[n, n] for n in range(len(self.points))]

    def get_points(self, face):
        p = self.projected_points
        match face:
            case "B":
                return [p[0], p[1], p[2], p[3]]
            case "F":
                return [p[4], p[5], p[6], p[7]]
            case "D":
                return [p[0], p[1], p[5], p[4]]
            case "U":
                return [p[2], p[3], p[7], p[6]]
            case "L":
                return [p[1], p[2], p[6], p[5]]
            case _:
                return [p[0], p[3], p[7], p[4]]

    def is_face_visible(self, face, reversed=1):
        match face:
            case "B":
                if self.r_pos[2] <= 0:
                    return False
            case "F":
                if self.r_pos[2] >= 0:
                    return False
            case "D":
                if self.r_pos[1] >= 0:
                    return False
            case "U":
                if self.r_pos[1] <= 0:
                    return False
            case "L":
                if self.r_pos[0] <= 0:
                    return False
            case _:
                if self.r_pos[0] >= 0:
                    return False
        if face in "BR":
            reversed = -1
        p1, p2, p3, _ = self.get_points(face)
        # Convert points to 3D NumPy arrays
        p1 = np.array([p1[0], p1[1], 0])
        p2 = np.array([p2[0], p2[1], 0])
        p3 = np.array([p3[0], p3[1], 0])
        # Calculate the normal vector of the face
        v1 = p2 - p1
        v2 = p3 - p1
        normal = np.cross(v1, v2) * reversed
        # The face is visible if the z component of the normal is negative
        return normal[2] < 0

    def draw_face(self, face):
        if not self.is_face_visible(face):
            return
        match face:
            case "U":
                r_pos = np.matrix((-self.r_pos[0], -self.r_pos[2]))
            case "D":
                r_pos = np.matrix((-self.r_pos[0], self.r_pos[2]))
            case "R":
                # Rotate r_pos 90 degrees for RL faces
                rotation_matrix = np.matrix([[0, 1], [-1, 0]])
                r_pos = np.dot(
                    rotation_matrix,
                    np.matrix((self.r_pos[1], self.r_pos[2])).T,
                ).T
            case "L":
                # Rotate r_pos 90 degrees for RL faces
                rotation_matrix = np.matrix([[0, 1], [-1, 0]])
                r_pos = np.dot(
                    rotation_matrix, np.matrix((self.r_pos[1], -self.r_pos[2])).T
                ).T
            case "F":
                # Rotate r_pos 180 degrees for FB faces
                rotation_matrix = np.matrix([[-1, 0], [0, -1]])
                r_pos = np.dot(
                    rotation_matrix, np.matrix((self.r_pos[0], self.r_pos[1])).T
                ).T
            case _:
                # Rotate r_pos 180 degrees for FB faces
                rotation_matrix = np.matrix([[-1, 0], [0, -1]])
                r_pos = np.dot(
                    rotation_matrix, np.matrix((-self.r_pos[0], self.r_pos[1])).T
                ).T
        r_pos //= 2
        cube_string = self.parent.to_string(True)
        face_index = FACE_ORDER.index(face)
        face_colors = cube_string[face_index * 9 : face_index * 9 + 9]
        x = r_pos[0, 0] + 1
        y = r_pos[0, 1] + 1
        color = face_colors[3 * y + x]
        Color(*self.parent.faces_colors[color])
        points = self.get_points(face)
        Mesh(
            vertices=[
                points[0][0],
                points[0][1],
                0,
                0,
                points[1][0],
                points[1][1],
                0,
                0,
                points[2][0],
                points[2][1],
                0,
                0,
                points[3][0],
                points[3][1],
                0,
                0,
            ],
            indices=[0, 1, 2, 2, 3, 0],
            mode="triangles",
        )
        Color(*self.parent.border_color)
        for i in range(4):
            Line(
                points=[
                    points[i][0],
                    points[i][1],
                    points[(i + 1) % 4][0],
                    points[(i + 1) % 4][1],
                ],
                width=self.parent.border,
                cap="round",
                joint="round",
            )

    def project_point(self, point, r_pos, angle, mult):
        rz, ry, rx = angle
        offset_point = point + r_pos
        # Apply the rotation matrices to the points
        rotated2d = np.dot(rz, offset_point.reshape((3, 1)))
        rotated2d = np.dot(ry, rotated2d)
        rotated2d = np.dot(rx, rotated2d)

        # Project the 3D points to 2D
        projected2d = np.dot(self.projection_matrix, rotated2d)

        x = int(projected2d[0, 0] * mult) + self.parent.center_x
        y = int(projected2d[1, 0] * mult) + self.parent.center_y

        return np.array([x, y])

    def render(self, angle, mult):
        # Update projected points
        for i, point in enumerate(self.points):
            self.projected_points[i] = self.project_point(
                point, self.r_pos, angle, mult
            )

        # Draw the faces of the cube
        for face in FACE_ORDER:
            self.draw_face(face)


class RubiksCube(Widget, Cube):
    angle = ListProperty([pi / 4, 5 * pi / 4, 0])
    """
    List of angles for rotation around the x, y, and z axes.
    """

    scale = NumericProperty(40)
    """
    Scale factor for the size of the cube.
    """

    border = NumericProperty(2)
    """
    Width of the border lines around each face.
    """

    allow_rotation = BooleanProperty(True)
    """
    Boolean to allow or disallow rotation of the cube.
    """

    max_y_rotation = BooleanProperty(False)
    """
    Boolean to limit the maximum rotation around the y-axis.
    """

    background_color = ColorProperty((0.9, 0.9, 0.9, 1))
    """
    Background color of the widget.
    """

    border_color = ColorProperty((0.1, 0.1, 0.1, 1))
    """
    Color of the border lines around each face.
    """

    frame_rate = NumericProperty(1 / 60)
    """
    Frame rate of updating cube
    """

    faces_colors = {
        "U": (1, 1, 1),
        "R": (1, 0.35, 0),
        "F": (0, 0.27, 0.68),
        "D": (1, 0.84, 0),
        "L": (0.72, 0.07, 0.20),
        "B": (0, 0.61, 0.28),
    }
    """
    Color of each face.
    """

    _last_touch_pos = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cubies = [
            Cubie(self, r_pos=[2 * x, 2 * y, 2 * z])
            for x in range(-1, 2)
            for y in range(-1, 2)
            for z in range(-1, 2)
            if (x, y, z) != (0, 0, 0)
        ]
        Clock.schedule_interval(self.update_cube, self.frame_rate)

    def _is_point_in_triangle(self, px, py, ax, ay, bx, by, cx, cy):
        # Calcul des barycentres pour vérifier si le point est dans le triangle
        denominator = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if denominator == 0:
            return False  # Triangle dégénéré

        a = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / denominator
        b = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / denominator
        c = 1 - a - b

        return 0 <= a <= 1 and 0 <= b <= 1 and 0 <= c <= 1

    def _is_touch_inside_face(self, touch_pos, face_points):
        """Vérifie si le toucher est à l'intérieur d'une face définie par 4 points."""
        x, y = touch_pos

        # Décompose la face en deux triangles
        (ax, ay), (bx, by), (cx, cy), (dx, dy) = face_points

        # Vérifie si le point est dans l'un des deux triangles
        return self._is_point_in_triangle(
            x, y, ax, ay, bx, by, cx, cy
        ) or self._is_point_in_triangle(x, y, ax, ay, cx, cy, dx, dy)

    def on_touch_down(self, touch: MotionEvent):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._last_touch_pos = touch.pos
            self._last_face_touch = None
            # Detect if a face is touch
            for cubie in self._cubies:
                if cubie.r_pos.count(0) != 2:
                    continue
                for face in FACE_ORDER:
                    if not cubie.is_face_visible(face):
                        continue
                    points = cubie.get_points(face).copy()
                    center = (points[0] + points[2]) / 2
                    face_coords = [None, None, None, None]
                    for i, p in enumerate(points):
                        face_coords[i] = center + 3 * (p - center)
                    if self._is_touch_inside_face(touch.pos, face_coords):
                        self._last_face_touch = face
            Window.set_system_cursor("hand")
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self and self.allow_rotation:
            dx = touch.pos[0] - self._last_touch_pos[0]
            dy = touch.pos[1] - self._last_touch_pos[1]

            self.angle[0] -= dy * 0.01
            if self.max_y_rotation or True:
                if self.angle[0] < pi:
                    self.angle[0] = min(self.angle[0], pi / 2)
                else:
                    self.angle[0] = max(self.angle[0], 3 * pi / 2)
            s = 1
            if pi / 2 < self.angle[0] < 3 * pi / 2:
                s = -1
            self.angle[1] += dx * 0.01 * s
            self.angle[0] %= 2 * pi
            self.angle[1] %= 2 * pi
            self.angle[2] %= 2 * pi

            self._last_touch_pos = touch.pos
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            if (
                self._last_face_touch
                and (touch.time_end - touch.time_start) < 0.3
                and touch.dpos == (0, 0)
            ):
                self.turn(self._last_face_touch)
            Window.set_system_cursor("arrow")
            return True
        return super().on_touch_up(touch)

    def update_cube(self, *args):
        # Define the rotation matrices
        rotation_z = np.matrix(
            [
                [cos(self.angle[2]), -sin(self.angle[2]), 0],
                [sin(self.angle[2]), cos(self.angle[2]), 0],
                [0, 0, 1],
            ]
        )

        rotation_y = np.matrix(
            [
                [cos(self.angle[1]), 0, sin(self.angle[1])],
                [0, 1, 0],
                [-sin(self.angle[1]), 0, cos(self.angle[1])],
            ]
        )

        rotation_x = np.matrix(
            [
                [1, 0, 0],
                [0, cos(self.angle[0]), -sin(self.angle[0])],
                [0, sin(self.angle[0]), cos(self.angle[0])],
            ]
        )

        rotation = (rotation_z, rotation_y, rotation_x)

        if self.width > self.height:
            size = self.height / 6
        else:
            size = self.width / 6

        mult = self.scale / 100 * size

        self.canvas.clear()
        with self.canvas:
            Color(*self.background_color)
            Rectangle(pos=self.pos, size=self.size)
            for cubie in self._cubies:
                cubie.render(rotation, mult)


class CubeApp(App):
    def build(self):
        return RubiksCube()


if __name__ == "__main__":
    CubeApp().run()
