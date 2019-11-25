from multiprocessing import Pool

import Wing


class InertiaXCalculator:

    wing = None

    def __init__(self, wing):
        self.wing = wing

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, Wing.stdrange)
        pool.close()
        pool.join()
        return results

    def value(self, y):
        return self.wing.moi_x(y)


class PolarInertiaCalculator:

    wing = None

    def __init__(self, wing):
        self.wing = wing

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, Wing.stdrange)
        pool.close()
        pool.join()
        return results

    def value(self, y):
        return self.wing.moi_polar(y)
