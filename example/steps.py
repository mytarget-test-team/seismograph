# -*- coding: utf-8 -*-

from seismograph import Case, Suite, Context, step


suite = Suite(__name__)


def step_performer(case, method, args, kwargs):
    return method(case, *args, **kwargs)


@suite.register
class ExampleStepByStepCase(Case):

    @step(1, 'Step one', performer=step_performer)
    def one(self):
        self.assertion.equal(1, 1)

    @step(2, 'Step two')
    def two(self):
        self.assertion.equal(2, 2)


@suite.register
class ExampleStepByStepCaseWithFlows(Case):

    __flows__ = (
        Context(num=1),
        Context(num=2),
        Context(num=3),
    )

    @step(1, 'Step one')
    def one(self, ctx):
        self.assertion.greater(ctx.num, 0)

    @step(2, 'Step two')
    def two(self, ctx):
        self.assertion.greater(ctx.num, 0)


if __name__ == '__main__':
    import seismograph
    seismograph.main()
