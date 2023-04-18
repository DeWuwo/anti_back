class StringUtils:
    @classmethod
    def replace_str(cls, old_string, start_index, end_index, replace_str: str):
        old_string = str(old_string)
        new_string = old_string[:start_index] + replace_str + old_string[end_index + 1:]
        return new_string

    @classmethod
    def replace_char(cls, old_string, index, char: str):
        old_string = str(old_string)
        new_string = old_string[:index] + char + old_string[index + 1:]
        return new_string

    @classmethod
    def find_str(cls, string: str, char: str):
        index_list = []
        for index in range(0, len(string)):
            if string[index] == char:
                index_list.append(index)
        return index_list

    @classmethod
    def find_char(cls, string: str, char: str):
        index_list = []
        for index in range(0, len(string)):
            if string[index] == char:
                index_list.append(index)
        return index_list


if __name__ == '__main__':
    a = '12315'
    print(StringUtils.find_char(a, '1'))
