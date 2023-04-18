from typing import List
from algorithm.utils import FileJson


class Compare:
    left: str
    right: str

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def get_anti_res(self):
        left: dict = FileJson.read_base_json(self.left)['res']['values']
        right: dict = FileJson.read_base_json(self.right)['res']['values']
        patterns = left.keys()
        return left, right, patterns

    def compare_ref(self):
        left: dict = FileJson.read_base_json(self.left)
        right: dict = FileJson.read_base_json(self.right)
        left_ref = set([int(l) for l in left.keys()])
        right_ref = set([int(r) for r in right.keys()])
        print(len(left_ref), len(right_ref))
        print(left_ref - right_ref)
        print('------------')
        print(right_ref - left_ref)
        print('------------')


def compare(left: dict, right: dict, patterns):
    repeat_count: dict = {}
    del_exas: dict = {}
    add_exas: dict = {}

    def match_example(exa1: List[dict], exa2: List[dict]):
        for rel1, rel2 in zip(exa1, exa2):
            if rel1['src']['category'] != rel2['src']['category'] or \
                    rel1['dest']['category'] != rel2['dest']['category'] or \
                    rel1['src']['qualifiedName'] != rel2['src']['qualifiedName'] or \
                    rel1['dest']['qualifiedName'] != rel2['dest']['qualifiedName'] or \
                    rel1['values'] != rel2['values']:
                return False
        return True

    for pattern in patterns:
        repeat_count[pattern] = {}
        del_exas[pattern] = {'count': 0, 'res': {}}
        add_exas[pattern] = {'count': 0, 'res': {}}
        old = left[pattern]['res']
        new = right[pattern]['res']
        for key, values in old.items():
            old_exa = old[key]['res']
            new_exa = new[key]['res']
            del_exas[pattern]['res'][key] = {'count': 0, 'res': []}
            add_exas[pattern]['res'][key] = {'count': 0, 'res': []}
            repeat_count[pattern][key] = {'left': old[key]['resCount'], 'right': new[key]['resCount'], 'repeat': 0,
                                          'repeat_map': []}
            left_match_index = set()
            right_match_index = set()
            for example1 in range(0, len(old_exa)):
                for example2 in range(0, len(new_exa)):
                    if example2 not in right_match_index and match_example(old_exa[example1]['values'],
                                                                           new_exa[example2]['values']):
                        left_match_index.add(example1)
                        right_match_index.add(example2)
                        repeat_count[pattern][key]['repeat'] += 1
                        repeat_count[pattern][key]['repeat_map'].append([str(example1) + '-' + str(example2)])
                        break
            del_index = set(range(len(old_exa))) - left_match_index
            add_index = set(range(len(new_exa))) - right_match_index
            for del_exa in del_index:
                del_exas[pattern]['res'][key]['res'].append(old_exa[del_exa])
                del_exas[pattern]['res'][key]['count'] += 1
                del_exas[pattern]['count'] += 1
            for add_exa in add_index:
                add_exas[pattern]['res'][key]['res'].append(new_exa[add_exa])
                add_exas[pattern]['res'][key]['count'] += 1
                add_exas[pattern]['count'] += 1

    FileJson.write_to_json('D:\\Honor\\test_res', repeat_count, 'test')
    FileJson.write_to_json('D:\\Honor\\test_res', del_exas, 'del_exa')
    FileJson.write_to_json('D:\\Honor\\test_res', add_exas, 'add_exa')


if __name__ == '__main__':
    cp = Compare('D:\\Honor\\match_res\\LineageOS\\base\\lineage_lineage18.1-18.1\\coupling-patterns\\res.json',
                 'D:\\Honor\\match_res\\LineageOS\\base\\lineage_lineage18.1-19.1\\coupling-patterns\\res.json')
    compare(*cp.get_anti_res())
