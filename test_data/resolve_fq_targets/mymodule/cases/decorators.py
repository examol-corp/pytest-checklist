def some_decor(f):
    def wrapper(*args, **kwargs):
        f(*args, **kwargs)

    return wrapper


class Some:
    @some_decor
    def for_test(self):
        pass
