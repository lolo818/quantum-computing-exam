import random
import sys

A_UP = 2
A_LOW = 0
B_UP = 3
B_LOW = -3
C_UP = 1
C_LOW = 0
SCOPE_NUM = 10
SCOPE_COVER_RATE = 0.5


def generate_exam(Qnum, index=0):
    exam = []
    scope = []
    for _ in range(Qnum):
        temp = {}
        temp["a"] = random.uniform(A_LOW, A_UP)
        temp["b"] = random.uniform(B_LOW, B_UP)
        temp["c"] = random.uniform(C_LOW, C_UP)
        exam.append(temp)

    for i in range(SCOPE_NUM):
        temp = []
        for j in range(Qnum - SCOPE_NUM):
            r = random.random()
            if r < SCOPE_COVER_RATE:
                temp.append(j)
        temp.append(Qnum - i - 1)
        scope.append(temp)

    # write to file
    with open(f"exam{index+1}.py", "w", encoding="utf-8") as f:
        f.write(f"exam = ({exam}, {scope})\n")


def main():

    if len(sys.argv) == 2:
        generate_exam(int(sys.argv[1]))
        return

    if len(sys.argv) == 3:
        for i in range(int(sys.argv[2])):
            generate_exam(int(sys.argv[1]), i)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generateExam.py <Q_NUM>")
        sys.exit(1)

    main()
