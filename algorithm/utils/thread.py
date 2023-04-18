import time
from typing import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from algorithm.utils import FileCSV


class MyThread:
    works: int
    func: Callable
    args: list

    def __init__(self, works: int, func, args: list):
        self.works = works
        self.func = func
        self.args = args

    def divide_works_args(self):
        step = int(len(self.args) / self.works)
        return [self.args[i * step: min(i * step + step, len(self.args))] for i in range(0, self.works + 1)]

    def start_th(self, need_index: bool, *args):
        with ThreadPoolExecutor(max_workers=self.works + 1) as th_pool:
            # for index, arg in enumerate(self.divide_works_args()):
            if need_index:
                res = [th_pool.submit(self.func, arg, *args, index) for index, arg in
                       enumerate(self.divide_works_args())]
            else:
                res = [th_pool.submit(self.func, arg, *args) for arg in self.divide_works_args()]
            return res

    def run(self):
        res = []
        for future in as_completed(self.start_th(True)):
            res.extend(future.result())
        return res

    def get_res(self,need_index, *args):
        return as_completed(self.start_th(need_index, *args))


def test(a, b):
    print(b)
    t1 = time.perf_counter()
    try:
        res = FileCSV.read_dict_from_csv(f'D:\\thTest\\final_ownership{b}.csv')
    except FileNotFoundError as e:
        res = [1, 2, 3]
    t2 = time.perf_counter()
    print(t2 - t1)
    res = res[0:1]
    return res


if __name__ == '__main__':
    t1 = time.perf_counter()
    resss = []
    res = MyThread(2, test, [0, 1]).start_th()
    print(len(res))
    for fu in as_completed(res):
        print('_________')
        print(fu.result())
    t2 = time.perf_counter()
    print(t2 - t1)
