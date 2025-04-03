import sys
from ttictoc import tic, toc
from GAexam import ENV


SCOPE_NUM = 10
EXAM_LIMIT = 10
ABILITY_LOW = -3  # 能力值下限
ABILITY_HIGH = 3  # 能力值上限
DIFFICULTY_UP = 2  # 考券平均難度上限
DIFFICULTY_LOW = -2  # 考券平均難度下限
DISCRIMINATION_CONSTR = 0.25  # 鑑別度限制
GENE_NUM = 1000
COVER_NUM = 10


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python3 env.py <exam_num>")

    exam_num = int(sys.argv[1])

    if len(sys.argv) == 2:
        for case in range(20):
            tic()
            print("Case: ", case)
            a = ENV(
                case=case,
                gene_num=GENE_NUM,
                gene_length=exam_num,
                ability_high=ABILITY_HIGH,
                ability_low=ABILITY_LOW,
                difficyly_up=DIFFICULTY_UP,
                difficyly_low=DIFFICULTY_LOW,
                spoce_num=SCOPE_NUM,
                exam_limit=EXAM_LIMIT,
                exam_num=exam_num,
                discrimination_limit=DISCRIMINATION_CONSTR,
            )

            for _ in range(100):
                a.iteration()

            a.check()
            print("Run Time: ", toc())
            print()

    else:
        case = int(sys.argv[2])
        tic()
        print("Case: ", case)
        a = ENV(
            case=case,
            gene_num=GENE_NUM,
            gene_length=exam_num,
            ability_high=ABILITY_HIGH,
            ability_low=ABILITY_LOW,
            difficyly_up=DIFFICULTY_UP,
            difficyly_low=DIFFICULTY_LOW,
            spoce_num=SCOPE_NUM,
            exam_limit=EXAM_LIMIT,
            exam_num=exam_num,
            discrimination_limit=DISCRIMINATION_CONSTR,
        )

        for _ in range(100):
            a.iteration()

        a.check()
        print("Run Time: ", toc())
        print()
