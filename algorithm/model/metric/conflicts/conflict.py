import csv
import os

from algorithm.utils import FileCSV


class Conflict:
    out_path: str
    conf_file: str
    conf_info: dict
    conf_info_sta: dict

    def __init__(self, file):
        self.out_path = file
        self.conf_file = os.path.join(file, 'conf/merge.csv')
        self.conf_info = {}
        self.conf_info_sta = {}

    def get_conf_files(self):
        conf_info: dict = {}
        if not os.path.exists(self.conf_file):
            return conf_info
        with open(self.conf_file, encoding='utf-8') as f:
            csv.field_size_limit(500 * 1024 * 1024)
            reader = csv.reader(f)
            next(reader)
            rows = [row for row in reader]
            conf_files_total = 0
            conf_times_total = len(rows)
            conf_loc_total = 0
            conf_times_by_file_total = 0

            for row in rows:
                conf_files = row[3]
                conf_loc = row[6]
                if int(row[2]) > 0:
                    files = [file[file.find('\'') + 1: file.rfind('\'')] for file in conf_files.split(',')]
                    locs = [int(loc) for loc in conf_loc[1: -1].split(',')]
                    for file, loc in zip(files, locs):
                        try:
                            conf_info[file]['times'] += 1
                            conf_info[file]['loc'] += loc
                        except KeyError:
                            conf_files_total += 1
                            conf_info[file] = {}
                            conf_info[file]['file'] = file
                            conf_info[file]['times'] = 1
                            conf_info[file]['loc'] = loc
                        conf_loc_total += loc
                        conf_times_by_file_total += 1

        self.conf_info = conf_info
        self.conf_info_sta = {'total_commits': conf_times_total, 'total_files': conf_files_total, 'loc': conf_loc_total,
                              'total_times_by_file': conf_times_by_file_total,
                              'average_times': float(conf_times_by_file_total / conf_files_total),
                              'average_loc': conf_loc_total / conf_files_total}
        for key, value in self.conf_info.items():
            self.conf_info[key].update({'statistic': self.conf_info_sta})
        self.get_conf_info_rank()
        return self.conf_info

    def get_conf_info_rank(self):
        conf_info = self.conf_info.copy()
        conf_file_num = len(conf_info)
        times_rank = sorted(conf_info.items(), key=lambda d: d[1]['times'], reverse=True)
        for index, item in enumerate(times_rank):
            self.conf_info[item[0]]['times_rank'] = f'{index + 1}/{conf_file_num}'

        loc_rank = sorted(conf_info.items(), key=lambda d: d[1]['loc'], reverse=True)
        for index, item in enumerate(loc_rank):
            self.conf_info[item[0]]['loc_rank'] = f'{index + 1}/{conf_file_num}'

        FileCSV.write_dict_to_csv(os.path.join(self.out_path, 'conf'), 'file-conf_rank',
                                  [value for _, value in self.conf_info.items()], 'w')


if __name__ == '__main__':
    Conflict('./new-aospa-sapphire-merge.csv').get_conf_files()
