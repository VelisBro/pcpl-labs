import argparse
import colorama
from lab_python_oop import Rectangle, Circle, Square


def main():
    parser = argparse.ArgumentParser(description="Геометрические фигуры")
    parser.add_argument("--variant", type=int, default=21)
    args = parser.parse_args()
    if args.variant <= 0:
        parser.error("номер варианта должен быть положительным")
    colorama.init()
    print("Вариант N = {}".format(args.variant))
    for figure in (Rectangle(args.variant, args.variant, "синий"),
                   Circle(args.variant, "зелёный"), Square(args.variant)):
        print(repr(figure))
    print("Внешний пакет: colorama {} (вызван init)".format(colorama.__version__))


if __name__ == "__main__":
    main()
