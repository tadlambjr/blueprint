class Repository:
    # port

    def __init__(self, dir, name):
        self._dir = dir
        self._name = name
        print(self)

    def __str__(self):
        return f'\tRepository: {self._name}'