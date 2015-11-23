# -*- coding: utf-8 -*-

from seismograph import Suite, Case, Context, assertion, step, flows


suite = Suite(__name__)


@suite.register
class SetFlowsWithClassAttribute(Case):

    __flows__ = (
        Context(num=1),
        Context(num=2),
    )

    def test_one(self, ctx):
        self.assertion.greater(ctx.num, 0)

    def test_two(self, ctx):
        self.assertion.greater(ctx.num, 0)


@flows(
    Context(num=1),
    Context(num=2),
)
@suite.register
class SetFlowsOnClassWithDecorator(Case):

    def test_one(self, ctx):
        self.assertion.greater(ctx.num, 0)

    def test_two(self, ctx):
        self.assertion.greater(ctx.num, 0)


@suite.register
class SetFlowsForOneTestOfCase(Case):

    @flows(
        Context(num=1),
        Context(num=2),
    )
    def test_with_flows(self, ctx):
        self.assertion.greater(ctx.num, 0)

    def test_without_flows(self):
        self.assertion.true(True)


@suite.register
class ExampleStepByStepCaseWithFlows(Case):

    __flows__ = (
        Context(num=1),
        Context(num=2),
    )

    @step(1, 'Step one')
    def one(self, ctx):
        self.assertion.greater(ctx.num, 0)

    @step(2, 'Step two')
    def two(self, ctx):
        self.assertion.greater(ctx.num, 0)


@suite.register(
    flows=(
        Context(num=1),
        Context(num=2),
    ),
)
def set_flows_for_function_test(case, ctx):
    case.assertion.greater(ctx.num, 0)


@flows(
    Context(num=1),
    Context(num=2),
)
@suite.register(static=True)
def set_flows_for_static_function_test(ctx):
    assertion.greater(ctx.num, 0)
