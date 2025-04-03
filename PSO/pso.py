import sys
import time
import math
import random
import matplotlib.pyplot as plt
from typing import Callable, Tuple, List

from exams.exams import exam_list
from HilbertCurve import HilbertCurve
from Particle import Particle

A_UP = 2
A_LOW = 0
B_UP = 3
B_LOW = -3
ABILITY_LOW = -3  # 能力值下限
ABILITY_HIGH = 3  # 能力值上限
D = 1.702  # 三參數項目反應模型的常數

exam_num_ = 100


class HilbertPSO:
    """基於希爾伯特曲線的PSO算法實現"""

    def __init__(
        self,
        fitness_func: Callable,
        dimension: int = 8,
        num_particles: int = 30,
        lower_bounds: int = None,
        upper_bounds: int = None,
        is_integer: bool = True,
        questions_num: int = 10,
        diff_upper: float = 2,
        diff_lower: float = -2,
        discrim_limit: float = 0.25,
        exams_num: int = 100,
        cover_num: int = 10,
        case: int = 0,
    ):
        """
        初始化PSO優化器

        參數:
            fitness_func: 適應度函數，接受N維位置並返回適應度值（越小越好）
            dimension: 問題空間的維度
            num_particles: 粒子數量
            lower_bounds: 一維的下界
            upper_bounds: 一維的上界
            is_integer: 是否為整數規劃問題
            hilbert_order: 希爾伯特曲線的階數
        """
        self.fitness_func = fitness_func
        self.dimension = dimension
        self.num_particles = num_particles
        self.is_integer = is_integer

        self.questions_num: int = questions_num
        self.diff_upper: float = diff_upper
        self.diff_lower: float = diff_lower
        self.discrim_limit: float = discrim_limit
        self.exams = exam_list[exams_num][case]
        self.exams_num: int = exams_num
        self.cover_num: int = cover_num
        self.bounds_1d = (lower_bounds, upper_bounds)

        # 開n次根號
        nd_lower_bounds = math.ceil(lower_bounds ** (1 / dimension))
        nd_upper_bounds = math.floor(upper_bounds ** (1 / dimension))

        # 創建n維空間的界限
        self.lower_bounds = [nd_lower_bounds] * self.dimension
        self.upper_bounds = [nd_upper_bounds] * self.dimension

        print(f"Lower bounds: {self.lower_bounds}")
        print(f"Upper bounds: {self.upper_bounds}")

        # 初始化希爾伯特曲線
        self.hilbert_curve = HilbertCurve(dimension=dimension)

        # 一維空間的界限

        # 初始化粒子群
        self.particles = [
            Particle(
                dimension,
                self.bounds_1d,
                self.hilbert_curve,
                self.lower_bounds,
                self.upper_bounds,
                self.questions_num,
                self.diff_upper,
                self.diff_lower,
                self.discrim_limit,
                self.exams_num,
                case,
                self.cover_num,
            )
            for _ in range(num_particles)
        ]

        # 全局最佳位置和適應度
        self.global_best_position_1d = 0
        self.global_best_position_nd = [0.0] * dimension
        self.global_best_fitness = float("inf")
        self.global_best_particle = None

        # PSO參數
        self.w = 0.7  # 慣性權重
        self.c1 = 1.6  # 認知參數
        self.c2 = 1.1  # 社會參數

        # 初始化粒子的適應度值
        self._evaluate_particles()

    def _evaluate_particles(self):
        """評估所有粒子的適應度"""
        for particle in self.particles:
            # 如果是整數規劃問題，則將位置向下取整
            position = particle.get_1d_position()

            # 計算適應度
            fitness = self.fitness_func(particle)

            # 更新個體最佳
            if fitness < particle.best_fitness:
                particle.best_fitness = fitness
                particle.best_position_1d = position
                particle.best_position_nd = particle.get_int_nd_position().copy()

                # 更新全局最佳
                if fitness < self.global_best_fitness:
                    self.global_best_fitness = fitness
                    self.global_best_position_1d = position
                    self.global_best_position_nd = particle.get_int_nd_position().copy()
                    self.global_best_particle = particle.copy()

    def _update_particles(self):
        """更新所有粒子的速度和位置"""
        for particle in self.particles:
            # 更新速度
            r1, r2 = random.random(), random.random()

            particle.velocity_nd = [
                self.w * v + self.c1 * r1 * (p_best - p) + self.c2 * r2 * (g_best - p)
                for v, p_best, p, g_best in zip(
                    particle.velocity_nd,
                    particle.best_position_nd,
                    particle.position_nd,
                    self.global_best_position_nd,
                )
            ]

            # 更新位置
            particle.position_nd = [
                p + v for p, v in zip(particle.position_nd, particle.velocity_nd)
            ]

            # 確保位置在界限內
            particle.correct()

            if not particle.is_legal():
                particle.correct()

    def optimize(
        self, max_iter: int = 100, verbose: bool = True
    ) -> Tuple[List[float], float, List[float]]:
        """
        執行PSO優化

        參數:
            max_iter: 最大迭代次數
            verbose: 是否顯示進度

        返回:
            (最佳位置, 最佳適應度值)
        """
        history = []  # 記錄每次迭代的最佳適應度

        for i in range(max_iter):
            # 更新粒子
            self._update_particles()

            # 評估粒子
            self._evaluate_particles()

            # 記錄最佳適應度
            history.append(self.global_best_fitness)

            # 顯示進度
            if verbose and (i + 1) % 10 == 0:
                print(
                    f"Iteration {i+1}/{max_iter}, Best fitness: {self.global_best_fitness}"
                )
                # print(f"Best position: {self.global_best_position_nd}")

        return (
            self.global_best_position_1d,
            self.global_best_position_nd,
            self.global_best_fitness,
            history,
            self.global_best_particle,
        )

    def visualize_optimization(self, history: List[float]):
        """
        視覺化優化過程

        參數:
            history: 每次迭代的最佳適應度記錄
        """
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, len(history) + 1), history)
        plt.title("Optimization Progress")
        plt.xlabel("Iteration")
        plt.ylabel("Best Fitness")
        plt.grid(True)
        plt.show()


def objective_function(pos: Particle) -> int:

    selected_exams = pos.get_selected_exams()
    diff = 0
    p = 0
    p += (len(selected_exams) - 10) ** 2
    p += 2 if len(selected_exams) != 10 else 0
    p += 0 if pos.check_cover() else 5

    for index in selected_exams:
        diff += pos.exams[0][index]["b"]
        if pos.exams[0][index]["a"] < pos.discrim_limit:
            p += 1

    if not pos.diff_lower <= diff / pos.questions_num <= pos.diff_upper:
        p += 5

    return sum([single_exam_range(pos.exams[0][index]) for index in selected_exams]) + p


# 常態分佈的累積機率函數
def cumulative_normal_distribution(x, mean=0, std_dev=1):
    return 0.5 * (1 + math.erf((x - mean) / (std_dev * math.sqrt(2))))


# 三參數項目反應模型
def icc_three_parameter(theta, a, b, c):
    z = D * a * (theta - b)
    p = c + (1 - c) * (1 / (1 + math.exp(-z)))
    return p


# 理想曲線與題目曲線的單點差異
def difficulty_difference(theta, exam):
    return cumulative_normal_distribution(theta) - icc_three_parameter(
        theta, exam["a"], exam["b"], exam["c"]
    )


def single_exam_range(exam):
    return sum(
        [
            difficulty_difference(theta, exam) ** 2
            for theta in range(ABILITY_LOW, ABILITY_HIGH + 1)
        ]
    )


def main(exam_num, exam_index):
    dimensions = 128
    upper_bounds = (1 << exam_num) - 1
    lower_bounds = 0

    # 創建PSO優化器實例
    pso = HilbertPSO(
        fitness_func=objective_function,
        dimension=dimensions,
        num_particles=500,
        lower_bounds=lower_bounds,
        upper_bounds=upper_bounds,
        exams_num=exam_num,
        case=exam_index,
    )

    # 進行優化
    tic = time.time()
    position, position_nd, fitness, history, particle = pso.optimize(
        max_iter=50, verbose=True
    )
    toc = time.time()

    # 輸出結果
    print(f"\n優化結果: {exam_num} {exam_index}")
    print(f"全局最佳位置: {position}")
    print(f"全局最佳位置: {position_nd}")
    print(f"全局最佳適應度值: {fitness}")
    print(f"執行時間: {toc - tic:.2f} 秒")
    print(f"選擇題目: {particle.get_selected_exams()}")

    if particle.is_legal():
        print()
        print(f"test {exam_index} passed")
        print()
        with open(f"result_{exam_num}.txt", "a", encoding="utf-8") as f:
            f.write(f"{fitness}\n")

        with open(f"result_{exam_num}_runtime.txt", "a", encoding="utf-8") as f:
            f.write(f"{toc - tic}\n")
    else:
        with open(f"result_{exam_num}.txt", "a", encoding="utf-8") as f:
            f.write("\n")

        with open(f"result_{exam_num}_runtime.txt", "a", encoding="utf-8") as f:
            f.write("\n")


# 示範如何使用PSO
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pso.py <exam_num> [exam_index]")
        sys.exit(1)

    exam_num_ = int(sys.argv[1])
    if len(sys.argv) > 2:
        exam_index_ = int(sys.argv[2])
        main(exam_num_, exam_index_)
    else:
        for case_ in range(20):
            main(exam_num_, case_)
