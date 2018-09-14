def subscript(var, sub):
    if '{_}' not in var:
        var += '{_}'
    return var.replace('{_}', '_{' + str(sub) + '}')


def row(var, r, c=None, transpose=False):
    if c is None:
        c = r
        sub = '{i}'
    else:
        sub = '{i}{r}' if transpose else '{r}{i}'
    return '&'.join(subscript(var, sub.format(r=r, i=i))
                    for i in range(1, c + 1))


def matrix(var, nrows, ncols, transpose=False):
    align = 'c' * ncols
    mat = '\\\\'.join([row(var, i, ncols, transpose)
                       for i in range(1, nrows + 1)])
    return '\n'.join([
        R'\left(\begin{array}{' + align + '}',
        mat,
        R'\end{array}\right)'
    ])


def vector(var, length, transpose=False):
    vec = row(var, length)
    if transpose:
        align = 'c' * length
        vec = vec.replace('&', '\\\\')
    else:
        align = 'c' * length
    return '\n'.join([
        R'\left(\begin{array}{' + align + '}',
        vec,
        R'\end{array}\right)'
    ])


def partial(f, x, frac=False):
    if frac:
        return (R'\frac{\partial ' + f + R'}{\partial\mathbf{'
                + x.upper() + '}}')
    else:
        return (R'\partial ' + f + R'/\partial\mathbf{'
                + x.upper() + '} ')


class Matrix:
    def __init__(self, var, nrows, ncols):
        self.var = var
        self.nrows = nrows
        self.ncols = ncols

    def __str__(self):
        return matrix(self.var, self.nrows, self.ncols)

    @property
    def T(self):
        return matrix(self.var, self.ncols, self.nrows, transpose=True)

    def shape(self):
        return (self.nrows, self.ncols)

    def partial(self, f, frac=False):
        if frac:
            var = R'\frac{\partial ' + f + R'}{\partial ' + self.var + '{_} }'
        else:
            var = R'\partial ' + f + R'/\partial ' + self.var + '{_} '
        return matrix(var, self.nrows, self.ncols)

    def spartial(self, f, frac=False):
        return partial(f, self.var, frac)


class Vector:
    def __init__(self, var, length):
        self.var = var
        self.length = length

    def __str__(self):
        return vector(self.var, self.length)

    @property
    def T(self):
        return vector(self.var, self.length, transpose=True)

    def shape(self):
        return (self.length,)

    def partial(self, f, frac=False):
        if frac:
            var = R'\frac{\partial ' + f + R'}{\partial ' + self.var + '{_} }'
        else:
            var = R'\partial ' + f + R'/\partial ' + self.var + '{_} '
        return vector(var, self.length)

    def spartial(self, f, frac=False):
        return partial(f, self.var, frac)


def main():
    x = Matrix('x', 2, 3)
    x.spartial('L')
