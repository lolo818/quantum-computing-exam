import math
import random
import sys
from gene import Gene
from exams.exams import exam_list

D = 1.702


class ENV:
    def __init__(
        self,
        case: int,
        gene_num: int,
        gene_length: int,
        ability_high: int,
        ability_low: int,
        difficyly_up: int,
        difficyly_low: int,
        spoce_num: int,
        exam_limit: int,
        exam_num: int,
        discrimination_limit: int,
    ) -> None:
        self.gene_num = gene_num
        self.gene_length = gene_length
        self.ability_high = ability_high
        self.ability_low = ability_low
        self.difficulty_up = difficyly_up
        self.difficulty_low = difficyly_low
        self.spoce_num = spoce_num
        self.exam_num = exam_num
        self.exam_limit = exam_limit
        self.discrimination_limit = discrimination_limit

        self.exams = exam_list[exam_num][case]
        self.genes = [
            Gene(
                case=case,
                exam_limit=exam_limit,
                exam_num=exam_num,
                gene_length=gene_length,
                discrimination_limit=discrimination_limit,
                difficyly_up=difficyly_up,
                difficyly_low=difficyly_low,
                scope_num=spoce_num,
            )
            for _ in range(self.gene_num)
        ]

    def cumulative_normal_distribution(self, x, mean=0, std_dev=1):
        return 0.5 * (1 + math.erf((x - mean) / (std_dev * math.sqrt(2))))

    def icc_three_parameter(self, theta, a, b, c):
        z = D * a * (theta - b)
        p = c + (1 - c) * (1 / (1 + math.exp(-z)))
        return p

    def difficulty_difference(self, theta, exam):
        result = self.cumulative_normal_distribution(theta) - self.icc_three_parameter(
            theta, exam["a"], exam["b"], exam["c"]
        )
        return result

    def single_exam_range(self, exam):
        arr = [
            self.difficulty_difference(theta, exam) ** 2
            for theta in range(self.ability_low, self.ability_high + 1)
        ]

        return sum(arr)

    def difficulty_constr(self, exam):
        return max(0, exam["b"] - self.difficulty_up) - max(
            0, self.difficulty_low - exam["b"]
        )

    def discrimination_constr(self, exam):
        return max(0, self.discrimination_limit - exam["a"])

    def calc_fitness(self, gene: Gene) -> int:
        result = 0
        exam_limit = 0
        difficulty = 0
        scope = 0

        for index, bit in enumerate(gene):
            if bit == "0":
                continue

            # 該考題的試題反應曲線與理想曲線的差異
            result += self.single_exam_range(self.exams[0][index])

            # 考題鑑別度度限制
            result += self.discrimination_constr(self.exams[0][index])

            # 考題平均難度
            difficulty += self.exams[0][index]["b"]

            exam_limit += 1

            for j in range(self.spoce_num):
                if index in self.exams[1][j]:
                    scope += 1 << j

        # 題數限制
        result += abs(self.exam_limit - exam_limit)

        # 平均難度限制
        result += (
            difficulty - self.difficulty_up
            if difficulty > self.difficulty_up
            else self.difficulty_low - difficulty
        )

        # 考卷範圍限制
        scope_ones = bin(scope).count("1")
        result += abs(scope_ones - self.spoce_num)

        return 1 / result

    def set_fitness(self):
        for gene in self.genes:
            gene.fitness = self.calc_fitness(gene)

    def iteration(self):
        self.set_fitness()
        self.genes = [self.mating() for _ in range(self.gene_num)]

    def mating(self):
        gene1: Gene
        gene2: Gene

        [gene1, gene2] = random.choices(
            self.genes, [gene.get_fitness() for gene in self.genes], k=2
        )

        return gene1 + gene2

    def show(self):
        result = self.get_result()

        # print("索引值: ", result)
        diff = sum([self.single_exam_range(self.exams[0][index]) for index in result])
        print("gap: ", diff)

    def check(self):
        result = self.get_result()
        count_ones = len(result)
        scope = 0
        difficulty = (
            sum([self.exams[0][index]["b"] for index in result]) / self.exam_limit
        )

        # print("索引值: ", result)
        diff = sum([self.single_exam_range(self.exams[0][index]) for index in result])
        print("gap: ", diff)

        for index in result:
            if self.exams[0][index]["a"] < self.discrimination_limit:
                print("鑑別度不符合: ", index)
                print(self.exams[0][index]["a"])

            for j in range(self.spoce_num):
                if index in self.exams[1][j]:
                    scope |= 1 << j

        scope_ones = bin(scope).count("1")

        if count_ones != self.exam_limit:
            print("題數不符合，目前題數: ", count_ones)

        if scope_ones != self.spoce_num:
            print("範圍不符合，目前涵蓋範圍: ", scope_ones)

        if difficulty > self.difficulty_up:
            print("平均難度過高: ", difficulty)

        if difficulty < self.difficulty_low:
            print("平均難度過低: ", difficulty)

    def get_result(self):
        diffs = [
            (
                sum(
                    [
                        (self.single_exam_range(self.exams[0][i]) if bit == "1" else 0)
                        for i, bit in enumerate(self.genes[index])
                    ]
                ),
            )
            for index in range(self.gene_num)
            # if self.genes[index].is_legal()
        ]

        min_index = diffs.index(min(diffs))
        result = self.genes[min_index].get_selected_exams()
        # print(self.genes[min_index].is_legal())
        # print("gene case", self.genes[min_index].case)
        return result
