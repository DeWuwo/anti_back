import time
import threading
from concurrent.futures import ThreadPoolExecutor


class DynamicThread:
    def __init__(self, func, tasks: list, max_thread_num, step, *func_arg):
        self.func = func
        self.tasks = tasks
        self.max_thread_num = max_thread_num
        self.step = step
        self.func_arg = func_arg
        self.complete_task = len(tasks)
        self.pool = ThreadPoolExecutor(max_workers=max_thread_num)
        self.cond = threading.Condition()
        self.res = -1
        self.th_id = 0

    def divide_works_args(self):
        ready_tasks = self.tasks[-self.step:]
        self.tasks = self.tasks[0: -self.step]
        self.th_id += 1
        return ready_tasks

    def res_collect(self, data):
        data_type = type(data)
        if data_type is list:
            if self.res == -1:
                self.res = []
            self.res.extend(data)
        if data_type is dict:
            if self.res == -1:
                self.res = {}
            self.res.update(data)

    def get_res(self, future):
        self.complete_task -= self.step
        self.res_collect(future.result())
        if self.tasks:
            task = self.divide_works_args()
            th = self.pool.submit(self.func, task, *self.func_arg, self.th_id)
            th.add_done_callback(self.get_res)
        else:
            if self.complete_task <= 0:
                self.cond.acquire()
                self.cond.notify()
                self.cond.release()
            return

    def start_tasks(self):
        for i in range(self.max_thread_num):
            if self.tasks:
                task = self.divide_works_args()
                th = self.pool.submit(self.func, task, *self.func_arg, self.th_id)
                th.add_done_callback(self.get_res)
            else:
                break

    def get_final_res(self):
        self.start_tasks()
        if self.complete_task <= 0:
            return self.res
        else:
            self.cond.acquire()
            self.cond.wait()
            self.cond.release()
            return self.res
