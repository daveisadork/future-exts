import future_exts  # noqa
import multiprocessing
import pytest
import threading

from concurrent.futures import Future, ThreadPoolExecutor


@pytest.fixture
def executor():
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as e:
        yield e


def test_can_create_completed_futures():
    # If I create a completed future
    future = Future.completed(42)

    # I expect its result to be set
    assert future.result() == 42


def test_sequencing_does_not_deadlock():
    with ThreadPoolExecutor(max_workers=1) as e:
        def _do_double(y):
            assert threading.current_thread() != main_thread
            return y * 2

        def double(x):
            return e.submit(_do_double, x)

        main_thread = threading.current_thread()
        future = double(1).then(double).then(double)
        assert future.result() == 8


def test_sequencing_propagates_exceptions(executor):
    # Given a function that raises an exception
    def f(x):
        raise Exception("some error occurred")

    # If I add it after a future
    future = executor.submit(lambda: 42).then(f)

    # I expect the exception to propagate when I get the future's result
    with pytest.raises(Exception):
        future.result()


def test_sequencing_propagates_deep_exceptions(executor):
    # Given a function that raises an exception
    def g(x):
        raise Exception("some error occurred")

    def f(x):
        return executor.submit(g, x)

    # If I add it after a future
    future = executor.submit(lambda: 42).then(f)

    # I expect the exception to propagate when I get the future's result
    with pytest.raises(Exception):
        future.result()


def test_can_sequence_futures(executor):
    # Given a function that doubles numbers using a thread pool
    def double(x):
        return executor.submit(lambda y: y * 2, x)

    # If I sequence a series of calls to that function
    future = double(10).then(double).then(double)

    # I expect my initial number to have been doubled 3 times
    assert future.result() == 80


def test_can_sequence_futures_using_normal_functions(executor):
    # If I attempt to sequence a future using a function that doesn't
    # return another future, I expect that to work as if it had.
    future = executor.submit(lambda: 21) \
                     .then(lambda x: x * 2)
    assert future.result() == 42
