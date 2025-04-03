class HilbertCurve:
    """
    超大整數希爾伯特曲線實現
    使用字符串和數學運算處理任意大小的整數
    """

    def __init__(self, dimension=4):
        """初始化超大整數希爾伯特曲線"""
        self.dimension = dimension

    def _to_base(self, n, base=2):
        """將整數轉換為指定進制的字符串"""
        if n == 0:
            return "0"

        digits = "0123456789abcdefghijklmnopqrstuvwxyz"
        result = ""

        while n > 0:
            result = digits[n % base] + result
            n //= base

        return result

    def _from_base(self, s, base=2):
        """將指定進制的字符串轉換為整數"""
        digits = "0123456789abcdefghijklmnopqrstuvwxyz"
        result = 0

        for c in s:
            result = result * base + digits.index(c)

        return result

    def d2xy(self, d):
        """從一維索引獲取多維坐標"""
        # 轉換為二進制字符串
        bin_str = self._to_base(d, 2)

        # 確保長度能被維度整除
        remainder = len(bin_str) % self.dimension
        if remainder > 0:
            bin_str = "0" * (self.dimension - remainder) + bin_str

        # 分配位元到各個維度
        coords = [0] * self.dimension

        # 直接分配每個維度的位元，避免位運算
        for i in range(len(bin_str)):
            dim = i % self.dimension
            bit_value = 1 if bin_str[i] == "1" else 0
            coords[dim] = coords[dim] * 2 + bit_value

        return coords

    def xy2d(self, coords):
        """從多維坐標獲取一維索引"""
        # 獲取每個坐標的二進制表示
        bin_strs = [self._to_base(coord, 2) for coord in coords]

        # 找出最長的二進制字符串長度
        max_len = max(len(s) for s in bin_strs)

        # 將所有二進制字符串填充到相同長度
        padded_strs = [s.zfill(max_len) for s in bin_strs]

        # 交織位元
        result_bin = ""
        for i in range(max_len):
            for dim in range(len(coords)):
                if i < len(padded_strs[dim]):
                    result_bin += padded_strs[dim][i]

        # 將二進制字符串轉換回整數
        return self._from_base(result_bin, 2) if result_bin else 0

    def map_1d_to_nd(self, position_1d):
        """一維到N維映射，無需浮點運算"""
        return self.d2xy(position_1d)

    def map_nd_to_1d(self, position_nd):
        """N維到一維映射，無需浮點運算"""
        return self.xy2d(position_nd)


def test_round_trip(hilbert, value):
    """測試希爾伯特曲線轉換是否能夠往返一致"""
    # 一維到N維再回到一維
    nd_pos = hilbert.map_1d_to_nd(value)
    back_to_1d = hilbert.map_nd_to_1d(nd_pos)

    print(f"原始值: {value}")
    print(f"轉換後: {back_to_1d}")
    print(f"差異:   {value - back_to_1d}")
    print("-" * 30)

    return value == back_to_1d


def main():
    """主測試函數"""
    dimension = 4
    hilbert = HilbertCurve(dimension=dimension)

    # 測試不同級別的大數
    test_values = [2**i for i in range(10, 601, 20)]
    for value in test_values:
        test_round_trip(hilbert, value)


if __name__ == "__main__":
    main()
