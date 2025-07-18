
from manim import *

class PythagoreanTheoremScene(Scene):
    def construct(self):
        a = 3
        b = 4
        c = 5

        square_a = Square(side_length=a, color=BLUE)
        square_b = Square(side_length=b, color=GREEN)
        square_c = Square(side_length=c, color=RED)

        formula = MathTex(r"a^2 + b^2 = c^2")

        group_squares = VGroup(square_a, square_b, square_c)
        group_squares.arrange(RIGHT, buff=1)

        self.play(Create(square_a), Create(square_b))
        self.wait(1)
        self.play(Create(square_c))
        self.wait(1)
        self.play(group_squares.arrange(DOWN, buff=1))
        self.wait(1)
        self.play(Write(formula))
        self.wait(2)
