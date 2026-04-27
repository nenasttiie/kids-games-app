import turtle


def setup_drawing():
    t = turtle.Turtle()
    t.ondrag(t.goto)
    screen = turtle.Screen()

    screen.title("Рисовалка с черепашкой")
    screen.bgcolor("white")
    screen.setup(700, 600)

    t.shape("turtle")
    t.pensize(3)
    t.speed(0)
    t.pencolor("deep pink")

    text_turtle = turtle.Turtle()
    text_turtle.hideturtle()
    text_turtle.penup()
    text_turtle.color("black")
    text_turtle.goto(-340, 270)
    text_turtle.write("Управление: C - очистить | R - красный | G - зелёный | B - синий | P - розовый | ↑/↓ - толщина",
                      font=("Arial", 10, "normal"))

    def draw(x, y):
        t.pendown()
        t.goto(x, y)

    def move_without_draw(x, y):
        t.penup()
        t.goto(x, y)
        t.pendown()

    def clear_all():
        t.clear()
        t.penup()
        t.home()
        t.pendown()
        t.pencolor("deep pink")

    def change_color_red():
        t.pencolor("red")

    def change_color_blue():
        t.pencolor("blue")

    def change_color_green():
        t.pencolor("green")

    def change_color_pink():
        t.pencolor("deep pink")

    t.ondrag(t.goto)
    screen.onclick(move_without_draw, 1)

    screen.onkey(clear_all, "c")
    screen.onkey(change_color_red, "r")
    screen.onkey(change_color_blue, "b")
    screen.onkey(change_color_green, "g")
    screen.onkey(change_color_pink, "p")
    screen.onkey(lambda: t.pensize(t.pensize() + 1), "Up")
    screen.onkey(lambda: t.pensize(max(1, t.pensize() - 1)), "Down")

    screen.listen()

    turtle.mainloop()


if __name__ == "__main__":
    setup_drawing()