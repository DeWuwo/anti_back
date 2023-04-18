import os
from algorithm.utils import FileJson, FileCSV


class CodeInfo:
    code_path: str
    pattern_type: str
    out_path: str
    target_dir: dict
    base_type: list

    def __init__(self, out_path, pattern_type, code_path, target_dir):
        self.code_path = code_path
        self.pattern_type = pattern_type
        self.out_path = out_path
        self.target_dir = target_dir
        self.base_type = ['java', 'aidl']

    def get_files(self):
        target = os.path.join(self.code_path, self.target_dir['path'])
        file_list = []
        for parent, dirs, files in os.walk(target):
            for f in files:
                if f.split('.')[-1] in self.base_type:
                    file_list.append(os.path.join(parent, f))

        return file_list

    # 统计一个的行数
    def count_line(self):
        total_count = 0
        files = self.get_files()
        # 把文件做二进制看待,read.
        for f in files:
            count = 0
            count += len(open(f, 'rb').readlines())
            total_count += count
        return {'pkg': self.target_dir['pkg'], 'file_count': len(files), 'loc': total_count}

    def get_anti_res(self):
        target = ''
        if self.target_dir['pkg']:
            pkg = self.target_dir['pkg']
            target = os.path.join(self.out_path, f'{pkg}\\{self.pattern_type}\\res.json')
        else:
            target = os.path.join(self.out_path, f'{self.pattern_type}\\res.json')

        res: dict = FileJson.read_base_json(target)['res']['values']

        status = {}
        status_count = {}
        for pattern, values in res.items():
            status[pattern] = []
            status_count[pattern] = 0
            for style_name, style_res in values['res'].items():
                status[pattern].append([style_res['resCount'], style_res['filterCount']])
                status_count[pattern] += style_res['resCount']
                status_count[pattern] += style_res['filterCount']
        return status, status_count

    def run(self):
        count_line = self.count_line()
        anti_count, anti_count_sum = self.get_anti_res()
        res = count_line.copy()
        res.update(anti_count)

        res2 = count_line.copy()
        res2.update(anti_count_sum)
        return res, res2

    @classmethod
    def get_anti_res_entity_count(cls, dir_path):
        res = []
        for dir in os.listdir(dir_path):
            temp = {'project': dir}
            json_res: dict = FileJson.read_base_json(os.path.join(dir_path, dir+'\\res.json'))['res']['values']
            entity_set = set()
            for pattern, values in json_res.items():
                for style_res in values['res']:
                    index = 0
                    for exam in style_res['res']:
                        if index == 10:
                            break
                        for rel in exam:
                            entity_set.add(rel['src']['id'])
                            entity_set.add(rel['dest']['id'])
            temp.update({'entity_count': len(entity_set)})
            res.append(temp)
        FileCSV.write_dict_to_csv(dir_path, 'cc', res, 'w')
        # target = ''
        # if self.target_dir['pkg']:
        #     pkg = self.target_dir['pkg']
        #     target = os.path.join(self.out_path, f'{pkg}\\{self.pattern_type}\\res.json')
        # else:
        #     target = os.path.join(self.out_path, f'{self.pattern_type}\\res.json')
        #
        # res: dict = FileJson.read_base_json(target)['res']['values']
        #
        # status = {}
        # status_count = {}
        # for pattern, values in res.items():
        #     status[pattern] = []
        #     status_count[pattern] = 0
        #     for style_name, style_res in values['res'].items():
        #         status[pattern].append([style_res['resCount'], style_res['filterCount']])
        #         status_count[pattern] += style_res['resCount']
        #         status_count[pattern] += style_res['filterCount']
        # return status, status_count


if __name__ == '__main__':
    CodeInfo.get_anti_res_entity_count('E:\\2022ASE\\datacheck')
