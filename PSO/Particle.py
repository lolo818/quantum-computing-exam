from typing import Tuple, List
from HilbertCurve import HilbertCurve
import random
import copy

from exams.exams import exam_list


class Particle:
    """PSO算法中的粒子類"""

    def __init__(
        self,
        dim: int,
        bounds: Tuple[int, int],
        hilbert_curve: HilbertCurve,
        lower_bounds: List,
        upper_bounds: List,
        questions_num: int,
        diff_upper: float,
        diff_lower: float,
        discrim_limit: float,
        exams_num: int,
        case: int,
        cover_num: int,
    ):
        """
        初始化粒子

        參數:
            dim: 維度
            bounds: 一維空間中的界限 (min, max)
            hilbert_curve: 希爾伯特曲線物件
            lower_bounds: N維空間中每個維度的下界
            upper_bounds: N維空間中每個維度的上界
        """
        self.position_1d = random.uniform(bounds[0], bounds[1])  # 一維位置
        self.hilbert_curve = hilbert_curve
        self.velocity_nd = [0.0] * dim
        self.lower_bounds = lower_bounds
        self.upper_bounds = upper_bounds
        self.position_nd = hilbert_curve.map_1d_to_nd(
            # 四捨五入
            int(self.position_1d + 0.5),
        )  # N維位置

        self.best_position_1d = self.position_1d  # 個體最佳一維位置
        self.best_position_nd = self.position_nd.copy()  # 個體最佳N維位置
        self.best_fitness = float("inf")  # 個體最佳適應度值

        self.questions_num: int = questions_num
        self.diff_upper: float = diff_upper
        self.diff_lower: float = diff_lower
        self.discrim_limit: float = discrim_limit
        self.exams = exam_list[exams_num][case]
        self.exams_num: int = exams_num
        self.cover_num: int = cover_num

    def get_int_nd_position(self) -> List[int]:
        # 四捨五入
        return [int(coord + 0.5) for coord in self.position_nd]

    def get_1d_position(self) -> int:
        return self.hilbert_curve.map_nd_to_1d(
            self.get_int_nd_position(),
        )

    def get_pos_bin(self) -> str:
        pos: int = self.position_1d
        if isinstance(pos, list):
            pos = pos[0]  # 提取單一元素

        if int(pos) > 2**self.exams_num - 1:
            pos %= 2**self.exams_num

        result = bin(int(pos))[2:].rjust(self.exams_num, "0")[::-1]
        return result

    def get_selected_exams(self) -> list:
        position_bin = self.get_pos_bin()
        return [index for index, bit in enumerate(position_bin) if bit == "1"]

    def is_legal(self) -> bool:
        select_exam = self.get_selected_exams()

        for exam in select_exam:
            if self.exams[0][exam]["a"] < self.discrim_limit:
                return False

        difficulty = (
            sum([self.exams[0][index]["b"] for index in select_exam])
            / self.questions_num
        )

        if not self.diff_lower <= difficulty <= self.diff_upper:
            return False

        if len(select_exam) != self.questions_num:
            return False

        for cover in self.exams[1]:
            if len(set(cover) & set(select_exam)) == 0:
                return False

        return True

    def add_gene(self, position: float) -> int:
        if isinstance(position, list):
            position = position[0]  # 提取單一元素

        for _ in range(self.exams_num):
            index = random.randint(0, self.exams_num - 1)
            if self.exams[0][index]["a"] >= self.discrim_limit:
                return int(position) | (1 << index)

    def sub_gene(self, position: float) -> int:
        if isinstance(position, list):
            position = position[0]  # 提取單一元素
        for _ in range(self.exams_num):
            index = random.randint(0, self.exams_num - 1)
            if self.exams[0][index]["a"] >= self.discrim_limit:
                return int(position) & ~(1 << index)

    def check_a(self) -> bool:
        for index in self.get_selected_exams():
            if self.exams[0][index]["a"] < self.discrim_limit:
                return False

        return True

    def fix_a(self) -> float:
        return int(
            "".join(
                [
                    (
                        "1"
                        if self.exams[0][index]["a"] >= self.discrim_limit
                        and bit == "1"
                        else "0"
                    )
                    for index, bit in enumerate(self.get_pos_bin())
                ]
            ),
            2,
        )

    def get_b(self) -> int:
        return (
            sum([self.exams[0][index]["b"] for index in self.get_selected_exams()])
            / self.exams_num
        )

    def check_b(self) -> bool:
        return self.diff_lower <= self.get_b() <= self.diff_upper

    def fix_b(self, position: int) -> int:
        selected_exams = self.get_selected_exams()

        remove_index = (
            max(selected_exams, key=lambda x: self.exams[0][x]["b"])
            if self.get_b() > self.diff_upper
            else min(selected_exams, key=lambda x: self.exams[0][x]["b"])
        )

        return position & ~(1 << remove_index)

    def check_cover(self) -> bool:
        selected_exams = self.get_selected_exams()

        for cover in self.exams[1]:
            if len(set(cover) & set(selected_exams)) == 0:
                return False

        return True

    def fix_cover(self, position: int) -> int:
        select_exams = self.get_selected_exams()
        uncover = [
            index
            for index in range(self.cover_num)
            if not set(select_exams) & set(self.exams[1][index])
        ]

        candidate = [exam for index in uncover for exam in self.exams[1][index]]
        add_exam = random.choice(candidate)

        r = [
            0.000001 + len(set(exam_arr) & set(select_exams + [add_exam]))
            for exam_arr in self.exams[1]
        ]

        select_exam_r = [
            min(
                [r[i] for i in range(self.cover_num) if index in self.exams[1][i]]
                + [self.cover_num]
            )
            for index in select_exams
        ]

        remove_exam = random.choices(select_exams, weights=select_exam_r, k=1)[0]
        new_position = int(position)
        new_position &= ~(1 << remove_exam)
        new_position |= 1 << add_exam

        return new_position

    def correct(self):
        new_position: int = self.position_1d

        if new_position >= (2 << self.exams_num):
            new_position %= 2 << self.exams_num

        for _ in range(100):
            if len(self.get_selected_exams()) < self.questions_num:
                new_position = self.add_gene(new_position)
                continue

            if len(self.get_selected_exams()) > self.questions_num:
                new_position = self.sub_gene(new_position)
                continue

            if not self.check_a():
                new_position = self.fix_a()
                continue

            if not self.check_b():
                new_position = self.fix_b(new_position)
                continue

            if not self.check_cover():
                new_position = self.fix_cover(new_position)
                continue

            self.position_1d = new_position
            self.position_nd = self.hilbert_curve.map_1d_to_nd(new_position)
            return

        self.position_1d = new_position
        self.position_nd = self.hilbert_curve.map_1d_to_nd(new_position)
        return

    def copy(self):
        """
        創建並返回粒子的深度複製
        """
        return copy.deepcopy(self)
