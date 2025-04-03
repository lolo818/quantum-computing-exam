from __future__ import annotations

import random

from exams.exams import exam_list


class Gene:
    def __init__(
        self,
        case: int,
        exam_limit: int,
        gene_length: int,
        discrimination_limit: int,
        difficyly_up: int,
        difficyly_low: int,
        scope_num: int,
        exam_num: int,
        num: int = None,
    ) -> Gene:
        self.case = case
        self.exam_num = exam_num
        self.exam_limit = exam_limit
        self.gene_length = gene_length
        self.discrimination_limit = discrimination_limit
        self.difficulty_up = difficyly_up
        self.difficulty_low = difficyly_low
        self.scope_num = scope_num
        self.exams = exam_list[exam_num][case]
        self.fitness = 0.001
        self.gene = (
            num if num is not None else random.randint(0, (1 << self.gene_length) - 1)
        )
        # if not self.correct():
        #     print("Gene Error")
        self.correct()
        # print(self.case)

    def __add__(self, other: Gene) -> Gene:
        mask = random.randint(0, (1 << self.gene_length) - 1)
        result = Gene(
            case=self.case,
            exam_limit=self.exam_limit,
            exam_num=self.exam_num,
            gene_length=self.gene_length,
            discrimination_limit=self.discrimination_limit,
            difficyly_up=self.difficulty_up,
            difficyly_low=self.difficulty_low,
            scope_num=self.scope_num,
            num=(self.gene & mask) | (other.gene & ~mask),
        )
        # if not result.correct():
        #     print("Gene Error")
        result.correct()

        return result

    def __str__(self) -> str:
        return bin(self.gene)[2:].zfill(self.gene_length)[::-1]

    def __iter__(self):
        return iter(str(self))

    def get_selected_exams(self):
        return [index for index, bit in enumerate(str(self)) if bit == "1"]

    def get_fitness(self):
        if self.fitness <= 0.001:
            return 0.001
        return self.fitness

    def get_gene_1_num(self):
        return str(self).count("1")

    def add_gene(self):
        for _ in range(self.gene_length):
            tt = random.randint(0, self.gene_length - 1)
            # print(tt)
            if self.exams[0][tt]["a"] < self.discrimination_limit:
                continue

            self.gene |= 1 << tt
            return True

        return False

    def sub_gene(self):
        tt = random.choice(self.get_selected_exams())
        self.gene &= ~(1 << tt)

        return False

    def check_a(self):
        for index in self.get_selected_exams():
            if self.exams[0][index]["a"] < self.discrimination_limit:
                return False

        return True

    def fix_a(self):
        self.gene = int(
            "".join(
                [
                    (
                        "1"
                        if self.exams[0][index]["a"] >= self.discrimination_limit
                        and bit == "1"
                        else "0"
                    )
                    for index, bit in enumerate(str(self))
                ]
            ),
            2,
        )

    def get_b(self):
        return (
            sum([self.exams[0][index]["b"] for index in self.get_selected_exams()])
            / self.gene_length
        )

    def check_b(self):
        return self.difficulty_low <= self.get_b() <= self.difficulty_up

    def fix_b(self):
        selected_exams = self.get_selected_exams()

        remove_index = (
            max(selected_exams, key=lambda x: self.exams[0][x]["b"])
            if self.get_b() > self.difficulty_up
            else min(selected_exams, key=lambda x: self.exams[0][x]["b"])
        )

        self.gene &= ~(1 << remove_index)

    def check_cover(self):
        selected_exams = self.get_selected_exams()

        scope = 0
        for j in self.exams[1]:
            scope <<= 1
            if set(selected_exams) & set(j):
                scope |= 1

        return bin(scope)[2:].count("1") >= self.scope_num

    def fix_cover(self):
        select_exam = self.get_selected_exams()
        uncover = [
            index
            for index in range(self.scope_num)
            if not set(select_exam) & set(self.exams[1][index])
        ]

        candidate = [exam for index in uncover for exam in self.exams[1][index]]
        add_exam = random.choice(candidate)

        r = [
            0.000001 + len(set(exam_arr) & set(select_exam + [add_exam]))
            for exam_arr in self.exams[1]
        ]

        select_exam_r = [
            min(
                [r[i] for i in range(self.scope_num) if index in self.exams[1][i]]
                + [self.scope_num]
            )
            for index in select_exam
        ]

        remove_exam = random.choices(select_exam, weights=select_exam_r, k=1)[0]
        self.gene &= ~(1 << remove_exam)
        self.gene |= 1 << add_exam

    def correct(self):
        for _ in range(self.get_gene_1_num() * 4):

            if self.get_gene_1_num() < self.exam_limit:
                self.add_gene()
                continue

            if self.get_gene_1_num() > self.exam_limit:
                self.sub_gene()
                continue

            if not self.check_a():
                self.fix_a()
                continue

            if not self.check_b():
                self.fix_b()
                continue

            if not self.check_cover():
                self.fix_cover()
                continue

            return True

        self.gene = random.randint(0, (1 << self.gene_length) - 1)
        self.correct()

    def is_legal(self):
        select_exam = self.get_selected_exams()
        # print(select_exam)

        for exam in select_exam:
            if self.exams[0][exam]["a"] < self.discrimination_limit:
                print("g鑑別度不符合: ", exam)
                return False

        difficulty = (
            sum([self.exams[0][index]["b"] for index in select_exam]) / self.exam_limit
        )

        if not self.difficulty_low <= difficulty <= self.difficulty_up:
            print("g平均難度不符合: ", difficulty)
            return False

        if self.get_gene_1_num() != self.exam_limit:
            print("g題數不符合: ", self.get_gene_1_num())
            return False

        scope = 0
        for index in select_exam:
            for j in range(self.scope_num):
                if index in self.exams[1][j]:
                    scope |= 1 << j

        scope_ones = bin(scope).count("1")

        if scope_ones != self.scope_num:
            print("g範圍不符合: ", scope_ones)
            return False

        return True


# if __name__ == "__main__":
#     a = Gene(num=2553289110102075119520317504, exam_num=4)
#     print(a.is_legal())
#     print(a.get_selected_exams())
