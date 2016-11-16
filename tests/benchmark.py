import time
import timeit

from ddtrace import Tracer, encoding

from .util import load_trace_file
from .test_tracer import get_test_tracer, get_benchmark_tracer


def trace_error(tracer):
    # explicit vars
    with tracer.trace("a", service="s", resource="r", span_type="t"):
        1 / 0


def benchmark_tracer_trace():
    REPEAT = 10
    NUMBER = 10000

    tracer = get_test_tracer()

    # testcase
    def trace(tracer):
        # explicit vars
        with tracer.trace("a", service="s", resource="r", span_type="t") as s:
            s.set_tag("a", "b")
            s.set_tag("b", 1)
            with tracer.trace("another.thing"):
                pass
            with tracer.trace("another.thing"):
                pass

    # benchmark
    print("## tracer.trace() benchmark: {} loops ##".format(NUMBER))
    timer = timeit.Timer(lambda: trace(tracer))
    result = timer.repeat(repeat=REPEAT, number=NUMBER)
    print("- trace execution time: {:8.6f}".format(min(result)))


def benchmark_tracer_wrap():
    REPEAT = 10
    NUMBER = 10000

    tracer = get_test_tracer()

    # testcase
    class Foo(object):
        @staticmethod
        @tracer.wrap()
        def s():
            return 0

        @classmethod
        @tracer.wrap()
        def c(cls):
            return 0

        @tracer.wrap()
        def m(self):
            return 0

    f = Foo()

    # benchmark
    print("## tracer.trace() wrapper benchmark: {} loops ##".format(NUMBER))
    timer = timeit.Timer(f.s)
    result = timer.repeat(repeat=REPEAT, number=NUMBER)
    print("- staticmethod execution time: {:8.6f}".format(min(result)))
    timer = timeit.Timer(f.c)
    result = timer.repeat(repeat=REPEAT, number=NUMBER)
    print("- classmethod execution time: {:8.6f}".format(min(result)))
    timer = timeit.Timer(f.m)
    result = timer.repeat(repeat=REPEAT, number=NUMBER)
    print("- method execution time: {:8.6f}".format(min(result)))


def benchmark_trace_encoding(REPEAT, NUMBER, TRACES, trace_filename):
    tracer = get_benchmark_tracer()

    # Create a fake trace and duplicate the reference in 15000 traces.
    # This should simulate the encoding of 15000 real traces
    fake_trace = load_trace_file(trace_filename, tracer)
    traces = [fake_trace for i in range(TRACES)]

    # testcase
    def encode_json(traces):
        encoding.encode_json(traces)

    def encode_msgpack(traces):
        encoding.encode_msgpack(traces)

    # benchmark
    print("## benchmark_trace_encoding for '{}': {} loops with {} traces with {} spans each ##".format(trace_filename, NUMBER, TRACES, len(fake_trace)))
    timer = timeit.Timer(lambda: encode_json(traces))
    result = timer.repeat(repeat=REPEAT, number=NUMBER)
    print("- encode_json execution time: {:8.6f}".format(min(result)))
    timer = timeit.Timer(lambda: encode_msgpack(traces))
    result = timer.repeat(repeat=REPEAT, number=NUMBER)
    print("- encode_msgpack execution time: {:8.6f}".format(min(result)))


if __name__ == '__main__':
    benchmark_tracer_wrap()
    benchmark_tracer_trace()
    benchmark_trace_encoding(10, 200, 150, './tests/simple_trace.json')
    benchmark_trace_encoding(10, 200, 150, './tests/complex_trace.json')
