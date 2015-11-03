# -*- coding: utf-8 -*-

from seismograph import Suite, Case, skip, skip_if, skip_unless


suite = Suite(__name__)


@suite.register(skip='reason')
def skip_function_test_on_register(case):
    # function test can be static. use static=True
    pass


@suite.register(skip='reason')
class SkipAllClass(Case):

    def test_one(self):
        pass

    def test_two(self):
        pass


@suite.register
class SkipDecoratorsExample(Case):

    @skip('reason')
    def test_two(self):
        pass

    @skip_if(1 == 1, 'reason')
    def test_two(self):
        pass

    @skip_unless(1 != 1, 'reason')
    def test_three(self):
        pass


@skip('reason')  # can be also skip_if, skip_unless
@suite.register
class SkipAllClassWithDecorator(Case):

    def test_one(self):
        pass


if __name__ == '__main__':
    import seismograph
    seismograph.main()
