class Compare:
    @classmethod
    def compare_list(cls, left: list, right: list):
        if set(left) != set(right):
            return False
        return True
