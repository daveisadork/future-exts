import sys

from concurrent import futures


class Future(futures.Future):
    @classmethod
    def completed(cls, res):
        """Wrap the given value in a Future.

        Parameters:
          res(object)

        Returns:
          Future: A new completed future containing the given value.
        """
        future = cls()
        future.set_result(res)
        return future

    @classmethod
    def sequence(cls, futures):
        """Convert a list of futures to a future of a list.

        Parameters:
          futures(list)

        Returns:
          Future: A future representing the list of futures'
          individual values.
        """
        if not futures:
            return Future.completed([])

        res_future = cls()
        res_futures = []

        def join(future):
            try:
                res_futures.append(future)
                if len(res_futures) == len(futures):
                    res_list = [f.result() for f in sorted(res_futures, key=lambda f: futures.index(f))]
                    res_future.set_result(res_list)
            except BaseException:
                _copy_exception(res_future)

        for future in futures:
            future.add_done_callback(join)

        return res_future

    def map(self, fn):
        """Map the result of this future using an arbitrary function.

        Parameters:
          fn(callable)

        Returns:
          Future: A new future.
        """
        res_future = type(self)()

        def transform(future):
            _copy_result(future, res_future, fn)

        self.add_done_callback(transform)
        return res_future

    def then(self, fn):
        """Sequence futures.

        Parameters:
          fn(callable)

        Returns:
          Future: A new future.
        """
        clazz = type(self)
        res_future = clazz()

        def transform(future):
            _copy_result(future, res_future)

        def flatten(future):
            try:
                res = future.result()
                if not isinstance(res, clazz):
                    return res_future.set_result(res)

                res.add_done_callback(transform)
            except BaseException:
                _copy_exception(res_future)

        future = self.map(fn)
        future.add_done_callback(flatten)
        return res_future


futures.Future = futures._base.Future = Future


def _copy_exception(target_future):
    exception, traceback = sys.exc_info()[1:]
    target_future.set_exception_info(exception, traceback)


def _copy_result(source_future, target_future, fn=None):
    try:
        exception, traceback = source_future.exception_info()
        if exception is None:
            if fn is not None:
                target_future.set_result(fn(source_future.result()))
            else:
                target_future.set_result(source_future.result())
        else:
            target_future.set_exception_info(exception, traceback)
    except BaseException:
        _copy_exception(target_future)
