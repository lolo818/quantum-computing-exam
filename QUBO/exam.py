import math
import os
from pyqubo import Array, Constraint
from QUBO import QUBOsolver
from exams.exams import exam_list

A_UP = 2
A_LOW = 0
B_UP = 3
B_LOW = -3
ABILITY_LOW = -3  # 能力值下限
ABILITY_HIGH = 3  # 能力值上限
D = 1.702  # 三參數項目反應模型的常數
DISCRIMINATION_CONSTR_SLACK_DECIMAL_PLACE_BIT_NUM = 3  # 鑑別度限制式slack小數點位數
QUANTUM_MODE = "BINARY"  # "SPIN" or "BINARY"

# 鑑別度懲罰項最大為0.0625^2 * Q_num = 0.004 * Q_num
# exams = exam_list[200][0]


class Exam:
    def __init__(
        self,
        q_num=10,
        difficulty_up=2,
        difficulty_low=-2,
        discrimination_limit=0.25,
        p=1,
        p_discrimination=5,
        p_difficulty=3,
        p_vertex_cover=0.3,
        p_question_num=900,
        num=100,
        case=0,
    ):
        self.result = {}
        self.q_num = q_num
        self.difficulty_up = difficulty_up
        self.difficulty_low = difficulty_low
        self.discrimination_limit = discrimination_limit
        self.p = p
        self.p_discrimination = p_discrimination
        self.p_diff = p_difficulty
        self.p_vertex_cover = p_vertex_cover * q_num
        self.p_question_num = p_question_num * q_num
        self.exams = exam_list[num][case]
        self.q_max = num

        # 限制式slack bit數
        self.difficulty_slack_bit_num = math.ceil(
            math.log((1 + B_UP - B_LOW) * q_num, 2)
        )
        self.discrimination_slack_bit_num = math.ceil(math.log(1 + A_UP - A_LOW, 2))
        self.exam_cover_slack_bit_num = math.ceil(math.log(1 + self.q_max, 2))

        self.nodes = Array.create("X", self.q_max, QUANTUM_MODE)

    # 常態分佈的累積機率函數
    def cumulative_normal_distribution(self, x, mean=0, std_dev=1):
        return 0.5 * (1 + math.erf((x - mean) / (std_dev * math.sqrt(2))))

    # 三參數項目反應模型
    def icc_three_parameter(self, theta, a, b, c):
        z = D * a * (theta - b)
        p = c + (1 - c) * (1 / (1 + math.exp(-z)))
        return p

    # 理想曲線與題目曲線的單點差異
    def difficulty_difference(self, theta, exam):
        return self.cumulative_normal_distribution(theta) - self.icc_three_parameter(
            theta, exam["a"], exam["b"], exam["c"]
        )

    # 單一考題在七個採樣點和理想曲線的差距平方和
    def single_exam_range(self, exam):
        return sum(
            [
                self.difficulty_difference(theta, exam) ** 2
                for theta in range(ABILITY_LOW, ABILITY_HIGH + 1)
            ]
        )

    # 單一題目鑑別度限制
    def single_exam_discrimination(self, j):
        # slack 小數點前的bits
        discrimination_slack_bits = Array.create(
            f"discrimination_slack_{j}", self.discrimination_slack_bit_num, QUANTUM_MODE
        )

        # slack 小數點後的bits
        discrimination_slack_decimal_place_bits = Array.create(
            f"discrimination_slack_decimal_place_{j}",
            DISCRIMINATION_CONSTR_SLACK_DECIMAL_PLACE_BIT_NUM,
            QUANTUM_MODE,
        )

        discrimination_slack = sum(  # slack小數點前的位數
            (2**i) * discrimination_slack_bits[i]
            for i in range(self.discrimination_slack_bit_num)
        ) + sum(  # slack 小數點後的位數
            (2 ** -(i + 1)) * discrimination_slack_decimal_place_bits[i]
            for i in range(DISCRIMINATION_CONSTR_SLACK_DECIMAL_PLACE_BIT_NUM)
        )

        return Constraint(
            self.nodes[j]
            * (self.exams[0][j]["a"] - discrimination_slack - self.discrimination_limit)
            ** 2,
            label=f"discrimination_constr_{j}",
        )

    # 單一題目覆蓋限制
    def exam_cover(self, j):
        # slack bits
        exam_cover_slack_bits = Array.create(
            f"exam_cover_slack{j}", self.exam_cover_slack_bit_num, QUANTUM_MODE
        )
        # slack
        exam_cover_slack = sum(
            (2**i) * exam_cover_slack_bits[i]
            for i in range(self.exam_cover_slack_bit_num)
        )
        return sum([self.nodes[i] for i in self.exams[1][j]]) - 1 - exam_cover_slack

    def f(self):
        return sum(
            self.nodes[j] * self.single_exam_range(self.exams[0][j])
            for j in range(self.q_max)
        )

    # 題目頻均難度限制
    def difficulty_constr(self):
        # 平均難度上限 slack 小數點前的 bits
        difficulty_upper_bits = Array.create(
            "difficulty_upper_slack", self.difficulty_slack_bit_num, QUANTUM_MODE
        )

        # 平均難度上限 slack 小數點後的 bits
        difficulty_upper_slack_decimal_place_bits = Array.create(
            "difficulty_upper_slack_decimal_place_bits",
            DISCRIMINATION_CONSTR_SLACK_DECIMAL_PLACE_BIT_NUM,
            QUANTUM_MODE,
        )

        # 平均難度下限 slack 小數點前的 bits
        difficulty_lower_bits = Array.create(
            "difficulty_lower_slack", self.difficulty_slack_bit_num, QUANTUM_MODE
        )

        # 平均難度下限 slack 小數點後的 bits
        difficulty_lower_slack_decimal_place_bits = Array.create(
            "difficulty_lower_slack_decimal_place_bits",
            DISCRIMINATION_CONSTR_SLACK_DECIMAL_PLACE_BIT_NUM,
            QUANTUM_MODE,
        )

        # 平均難度上限 slack
        difficulty_upper_slack = sum(
            2**i * difficulty_upper_bits[i]
            for i in range(self.difficulty_slack_bit_num)
        ) + sum(
            (2 ** -(i + 1)) * difficulty_upper_slack_decimal_place_bits[i]
            for i in range(DISCRIMINATION_CONSTR_SLACK_DECIMAL_PLACE_BIT_NUM)
        )

        # 平均難度下限 slack
        difficulty_lower_slack = sum(
            2**i * difficulty_lower_bits[i]
            for i in range(self.difficulty_slack_bit_num)
        ) + sum(
            (2 ** -(i + 1)) * difficulty_lower_slack_decimal_place_bits[i]
            for i in range(DISCRIMINATION_CONSTR_SLACK_DECIMAL_PLACE_BIT_NUM)
        )

        # 平均難度
        difficulty = sum(
            [node * exam["b"] for (node, exam) in zip(self.nodes, self.exams[0])]
        )

        # 平均難度上限限制式
        difficulty_upper_constr = Constraint(
            (difficulty + difficulty_upper_slack - (self.difficulty_up * self.q_num))
            ** 2,
            label="difficulty_upper_constr",
        )

        # 平均難度下限限制式
        difficulty_lower_constr = Constraint(
            (difficulty - difficulty_lower_slack - (self.difficulty_low * self.q_num))
            ** 2,
            label="difficulty_lower_constr",
        )

        return self.p_diff * (difficulty_upper_constr + difficulty_lower_constr)

    # 題目覆蓋限制
    def exam_cover_constr(self):
        return self.p_vertex_cover * Constraint(
            sum(self.exam_cover(i) ** 2 for i in range(len(self.exams[1]))),
            label="exam_cover_constr",
        )

    # 題目數量限制
    def question_num_constr(self):
        return self.p_question_num * Constraint(
            (sum(self.nodes) - self.q_num) ** 2,
            label="question_num_constr",
        )

    # 題目鑑別度限制
    def discrimination_constr(self):
        return self.p_discrimination * sum(
            [self.single_exam_discrimination(i) for i in range(self.q_max)]
        )

    def generate(self, runs=50, sweep=21000, mode="compal_gpu"):
        h = (
            self.f() * self.p
            + self.difficulty_constr()
            + self.exam_cover_constr()
            + self.question_num_constr()
            + self.discrimination_constr()
        )

        model = h.compile()

        result = QUBOsolver.processQUBO(model, mode, runs, sweep)

        self.result = {
            "solve": result["solve"],
            "broken_constrs": 0,
            "run_time": result["run_time"],
        }

        return self.result

    def get_gap(self):
        gap = 0

        for i in range(self.q_max):
            if self.result["solve"][f"X[{i}]"] == 1:
                gap += float(self.single_exam_range(self.exams[0][i]))
        return gap

    def check_result(self):
        # if len(self.result["broken_constrs"]) != 0:
        #     print("Broken constraints: ", len(self.result["broken_constrs"]))

        selected_exams = [
            i for i in range(self.q_max) if self.result["solve"][f"X[{i}]"] == 1
        ]
        print("Selected exams: ", selected_exams)

        if len(selected_exams) != self.q_num:
            print("題數不符合要求:", len(selected_exams))

        for e in selected_exams:
            if self.exams[0][e]["a"] <= self.discrimination_limit:
                print("鑑別度不符合要求:", e)

        difficulty = sum([self.exams[0][i]["b"] for i in selected_exams])
        if (
            difficulty > self.difficulty_up * self.q_num
            or difficulty < self.difficulty_low * self.q_num
        ):
            print("難度不符合要求")

        scope = 0
        for j in self.exams[1]:
            scope <<= 1
            if set(selected_exams) & set(j):
                scope |= 1

        if bin(scope).count("1") != len(self.exams[1]):
            print("覆蓋不符合要求:", bin(scope).count("1"))

    def show_bits(self):
        print("Result:")
        for i in range(self.q_max):
            print(f"X[{i}]: {self.result['solve'][f'X[{i}]']}")
        print()

        print("Difficulty upper slack bits:")
        for i in range(self.difficulty_slack_bit_num):
            print(
                f"difficulty_upper_slack[{i}]: {self.result['solve'][f'difficulty_upper_slack[{i}]']}"
            )

        for i in range(DISCRIMINATION_CONSTR_SLACK_DECIMAL_PLACE_BIT_NUM):
            print(
                f"difficulty_upper_slack_decimal_place[{i}]: {self.result['solve'][f'difficulty_upper_slack_decimal_place_bits[{i}]']}"
            )
        print()

        print("Difficulty lower slack bits:")
        for i in range(self.difficulty_slack_bit_num):
            print(
                f"difficulty_lower_slack[{i}]: {self.result['solve'][f'difficulty_lower_slack[{i}]']}"
            )

        for i in range(DISCRIMINATION_CONSTR_SLACK_DECIMAL_PLACE_BIT_NUM):
            print(
                f"difficulty_lower_slack_decimal_place[{i}]: {self.result['solve'][f'difficulty_lower_slack_decimal_place_bits[{i}]']}"
            )
        print()

        print("cover slack bits:")
        for i in range(len(self.exams[1])):
            for j in range(self.exam_cover_slack_bit_num):
                print(
                    f"exam_cover_slack_{i}[{j}]: {self.result['solve'][f'exam_cover_slack{i}[{j}]']}"
                )
            print("")
        print()

        print("discrimination slack bits:")
        for i in range(self.q_max):
            for j in range(self.discrimination_slack_bit_num):
                print(
                    f"discrimination_slack_{i}[{j}]: {self.result['solve'][f'discrimination_slack_{i}[{j}]']}"
                )

            for j in range(DISCRIMINATION_CONSTR_SLACK_DECIMAL_PLACE_BIT_NUM):
                print(
                    f"discrimination_slack_decimal_place_{i}[{j}]: {self.result['solve'][f'discrimination_slack_decimal_place_{i}[{j}]']}"
                )
            print("")


def run(exam_index, case_index):
    print(f"Exam {exam_index}, case {case_index}")
    the_exam = Exam(num=exam_index, case=case_index)
    the_exam.generate(runs=300, sweep=2000, mode="compal_new")
    print("gap: ", the_exam.get_gap())
    the_exam.check_result()
    print("run time: ", the_exam.result["run_time"])
    print()

    with open(f"result_{exam_index}.txt", "a", encoding="utf-8") as f:
        f.write(f"{the_exam.get_gap()}\n")

    with open(f"runtime_{exam_index}.txt", "a", encoding="utf-8") as f:
        f.write(f"{the_exam.result['run_time']}\n")


def main():
    the_num = int(os.sys.argv[1])

    if len(os.sys.argv) == 2:
        for case in range(20):
            run(the_num, case)
    else:
        case = int(os.sys.argv[2])
        for _ in range(5):
            run(the_num, case)


if __name__ == "__main__":
    if len(os.sys.argv) < 2:
        print("Usage: python exam.py <exam_index> [case_index]")
        os.sys.exit(1)

    main()
