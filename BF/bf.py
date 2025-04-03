import os
import math
from ttictoc import tic, toc
from exams.exams import exam_list

SCOPE_NUM = 10
EXAM_NUM = 10
exam_max = 20
ABILITY_LOW = -3  # 能力值下限
ABILITY_HIGH = 3  # 能力值上限
DIFFICULTY_UP = 2  # 考券平均難度上限
DIFFICULTY_LOW = -2  # 考券平均難度下限
DISCRIMINATION_CONSTR = 0.25  # 鑑別度限制
D = 1.702
GENE_NUM = 1000
exam_max = 0

def get_fitness(i):
    e = bin(i)[2:].zfill(exam_max)[::-1]  
    selected_exams = [i for i in range(exam_max) if e[i] == "1"]

    if len(selected_exams) != EXAM_NUM:
        # print("exam num error")
        return 0
    
    result = 0
    scope = 0
    difficulty = 0

    for j in exams[1]:
        scope <<= 1
        if set(selected_exams) & set(j):
            scope |= 1

    if bin(scope).count("1") != SCOPE_NUM:
        # print("scope error")
        return 0
    
    for index in selected_exams:
        if exams[0][index]["a"] < DISCRIMINATION_CONSTR:
            # print("discrimination error")
            return 0
        
        difficulty += exams[0][index]["b"]
        result += single_exam_range(exams[0][index])

    difficulty /= EXAM_NUM
        
    if difficulty > DIFFICULTY_UP or difficulty < DIFFICULTY_LOW:
        # print("difficulty error")
        return 0
    
    return result

def cumulative_normal_distribution(x, mean=0, std_dev=1):
    return 0.5 * (1 + math.erf((x - mean) / (std_dev * math.sqrt(2))))

def icc_three_parameter(theta, a, b, c):
    z = D * a * (theta - b)
    p = c + (1 - c) * (1 / (1 + math.exp(-z)))
    return p

def difficulty_difference(theta, exam):
    result = cumulative_normal_distribution(theta) - icc_three_parameter(
        theta, exam["a"], exam["b"], exam["c"]
    )
    return result

def single_exam_range(exam):
    arr = [
        difficulty_difference(theta, exam) ** 2
        for theta in range(ABILITY_LOW, ABILITY_HIGH + 1)
    ] 

    return sum(arr)

def bf():
    result = []
    for i in range(1 << exam_max):
        result.append(get_fitness(i))

    answer = min([ x for x in result if x != 0])
    e = bin(result.index(answer))[2:].zfill(exam_max)
    selected_exams = [i for i in range(exam_max) if e[i] == "1"]
    # print(selected_exams)
    # answer_index = result.index(answer)

    print(answer)

if __name__ == "__main__":
    if len(os.sys.argv) < 2:
        print("Usage: python bf.py [exam_max]")
        os.sys.exit(1)

    exam_max = int(os.sys.argv[1])

    if len(os.sys.argv) == 2:
        for case in range(20):
            print(f"Case {case}")
            tic()
            exams = exam_list[exam_max][case]
            bf()
            print("Run Time:", toc())

    else:
        case = int(os.sys.argv[2])
        tic()
        exams = exam_list[exam_max][case]
        bf()
        print("Run Time:", toc())