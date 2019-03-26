# # API

# ## Parser

from pheasant import Parser


# -
class A:
    def render_number(self, context, splitter, parser):
        number = int(context["number"])
        yield context["number"] * number

    def render_plus(self, context, splitter, parser):
        cell = next(splitter)
        if cell.match:
            yield "[" + cell.parse(splitter, parser) + "]"
        else:
            yield "<" + cell.source + ">"

    def render_begin(self, context, splitter, parser):
        source = ""
        while True:
            cell = next(splitter)
            if cell.source == "]":
                source = str(int(source) + 4)
                splitter.send(source)
                break
            elif "1" <= cell.source <= "9":
                source += cell.source
            else:
                yield parser.parse("+" + cell.source)

    def render_end(self, context, splitter, parser):
        yield ""


# -
parser = Parser()
a = A()

number_pattern = r"(?P<number>[1-9])"
plus_pattern = r"(?P<plus>\+)"
begin_pattern = r"(?P<begin>\[)"
end_pattern = r"(?P<begin>\])"

parser.register(number_pattern, a.render_number)
parser.register(plus_pattern, a.render_plus)
parser.register(begin_pattern, a.render_begin)
parser.register(end_pattern, a.render_end)

parser.patterns

# -
parser.parse("3")

# -
parser.parse("+2")


# -
parser.parse("+++5")


# -
parser.parse("a[x3y2]")
