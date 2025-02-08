import random, kociemba


SOLVED_CUBE_STRING = "UUUUUUUURRRRRRRRFFFFFFFFDDDDDDDDLLLLLLLLBBBBBBBB"
FACE_ORDER = "URFDLB"


class Cube:
    def __init__(self, patternstring: str | None = SOLVED_CUBE_STRING) -> None:
        """Initialize the cube"""
        if patternstring:
            self.from_string(patternstring)

    def _get_face(self, face: str) -> str:
        index = FACE_ORDER.index(face)
        return self._cube_string[index * 8 : (index + 1) * 8]

    def _get_side(self, face: str, side: str) -> str:
        face = self._get_face(face)
        match side:
            case "U":
                return face[:3]
            case "R":
                return face[2:5]
            case "D":
                return face[4:7]
            case "L":
                return face[6:8] + face[0]

    def _set_side(self, face: str, side: str, pos: str) -> None:
        index = FACE_ORDER.index(face) * 8
        match pos:
            case "U":
                self._cube_string = (
                    self._cube_string[:index] + side + self._cube_string[index + 3 :]
                )
            case "R":
                self._cube_string = (
                    self._cube_string[: index + 2]
                    + side
                    + self._cube_string[index + 5 :]
                )
            case "D":
                self._cube_string = (
                    self._cube_string[: index + 4]
                    + side
                    + self._cube_string[index + 7 :]
                )
            case "L":
                self._cube_string = (
                    self._cube_string[:index]
                    + side[2]
                    + self._cube_string[index + 1 : index + 6]
                    + side[:2]
                    + self._cube_string[index + 8 :]
                )

    def _face_rotate(self, face: str) -> None:
        index = FACE_ORDER.index(face) * 8
        self._cube_string = (
            self._cube_string[:index]
            + self._cube_string[index + 6 : index + 8]
            + self._cube_string[index : index + 6]
            + self._cube_string[index + 8 :]
        )

    def from_string(self, patternstring: str) -> bool:
        """Construct a cube from a string."""
        if len(patternstring) < 48:
            raise ValueError(
                "Cube definition string "
                + patternstring
                + " contains less than 48 facelets."
            )
        elif len(patternstring) > 48:
            raise ValueError(
                "Cube definition string "
                + patternstring
                + " contains more than 48 facelets."
            )
        for i in FACE_ORDER:
            if patternstring.count(i) != 8:
                raise ValueError(
                    "Cube definition string "
                    + patternstring
                    + " does not contain exactly 8 facelets of each color."
                )
        self._cube_string = patternstring
        # Raise an error if the string is not correct
        kociemba.solve(self.to_kociemba())

    def to_string(self, kociemba=False) -> str:
        """Return the string of the cube"""
        if kociemba:
            return self.to_kociemba()
        else:
            return self._cube_string

    def to_kociemba(self) -> str:
        """Return a the cube_string based on kociemba input string"""
        faces = []
        for i in range(0, len(self._cube_string), 8):
            faces.append(self._cube_string[i : i + 8])
        f = ""
        for i, face in enumerate(faces):
            f += face[0:3]
            f += face[7]
            f += FACE_ORDER[i]
            f += face[3]
            f += face[6]
            f += face[5]
            f += face[4]
        return f

    def is_solve(self) -> bool:
        """Return if True the cube is solve"""
        return self._cube_string == SOLVED_CUBE_STRING

    def turn(self, move: str) -> None:
        """Turn a face of the cube"""
        if len(move) == 1:
            f = move
            nb = "1"
        else:
            f, nb = move
        if nb != "1":
            if nb == "2":
                self.turn(f + "1")
            else:
                self.turn(f + "2")
        table = {
            "U": ("BRFL", "UUUU"),
            "R": ("BDFU", "LRRR"),
            "F": ("URDL", "DLUR"),
            "D": ("BLFR", "DDDD"),
            "L": ("BUFD", "RLLL"),
            "B": ("DRUL", "DRUL"),
        }[f]
        self._face_rotate(f)
        sides = [self._get_side(table[0][i], table[1][i]) for i in range(4)]
        for i, f in enumerate(table[0]):
            self._set_side(f, sides[i - 1], table[1][i])

    def solve(self, patternstring: str | None = None, max_depth: int = 24) -> str:
        """Solve a cube and return the solution"""
        if self.is_solve():
            return "Already solve"
        return kociemba.solve(self._cube.to_kociemba(), patternstring, max_depth)

    def random(self, nb: int = random.randint(20, 30)) -> None:
        """Randomize the cube"""
        for i in range(nb):
            f = FACE_ORDER[random.randint(0, 5)]
            n = random.randint(1, 3)
            self.turn(str(f) + str(n))
