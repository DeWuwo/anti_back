import os
from typing import List
from collections import defaultdict
from algorithm.utils import FileCSV, StringUtils


class SDKApi:
    code_path: str
    out_path: str
    api_path: str

    def __init__(self, code_path, out_path):
        self.code_path = code_path
        self.out_path = out_path
        self.api_path = os.path.join(code_path, 'api/current.txt') if os.path.exists(
            os.path.join(code_path, 'api/current.txt')) else \
            os.path.join(code_path, 'core/api/current.txt')

    def get_apis(self):
        apis = defaultdict(list)
        stack: List[str] = []
        with open(self.api_path, 'r', encoding='utf-8') as f:
            for line_data in f:
                line_str = str(line_data).strip()
                self.get_api_from_line(apis, stack, line_str)
        api_data = []
        for _, v in apis.items():
            api_data.extend(v)
        FileCSV.write_dict_to_csv(self.out_path, 'sdk_apis', api_data, 'w')
        return apis

    def get_api_from_line(self, apis, stack, line_str):
        line = line_str.split(' ')
        if line[0] == 'package' and line[2] == '{':
            stack.append(line[1])
        elif 'class' in line and '{' in line:
            name = line[line.index('class') + 1]
            if '<' in name:
                name = name[0: name.find('<')]
            stack.append(name)
            api_name = '.'.join(stack)
            apis[api_name].append({'name': api_name, 'params': ''})
        elif 'interface' in line and '{' in line:
            name = line[line.index('interface') + 1]
            if '<' in name:
                name = name[0: name.find('<')]
            stack.append(name)
            api_name = '.'.join(stack)
            apis[api_name].append({'name': api_name, 'params': ''})
        elif '@interface' in line and '{' in line:
            name = line[line.index('@interface') + 1]
            if '<' in name:
                name = name[0: name.find('<')]
            stack.append(name)
            api_name = '.'.join(stack)
            apis[api_name].append({'name': api_name, 'params': ''})
        elif 'enum' in line and '{' in line:
            name = line[line.index('enum') + 1]
            if '<' in name:
                name = name[0: name.find('<')]
            stack.append(name)
            api_name = '.'.join(stack)
            apis[api_name].append({'name': api_name, 'params': ''})
        elif '}' in line:
            stack.pop()
        else:
            pre_name = '.'.join(stack) + '.'
            if 'ctor' in line:
                ctor = ''
                for content in line:
                    if '(' in content and content[0] != '@':
                        ctor = content
                        break
                name = ctor[max(ctor.rfind('.') + 1, 0): ctor.find('(')]
                api_name = pre_name + name
                api_param = self.fetch_param(line_str[line_str.rfind(name + '(') + len(name) + 1: line_str.rfind(')')])
                apis[api_name].append({'name': api_name, 'params': ' '.join(api_param)})
            elif 'method' in line:
                method = ''
                for content in line:
                    if '(' in content and content[0] != '@':
                        method = content
                        break
                name = method[0: method.find('(')]
                api_name = pre_name + name
                api_param = self.fetch_param(
                    line_str[line_str.rfind(name + '(') + len(name) + 1: line_str.rfind(')')])
                apis[api_name].append({'name': api_name, 'params': ' '.join(api_param)})
            elif 'field' in line:
                if '=' in line:
                    field = line[line.index('=') - 1]
                else:
                    field = line[-1][0: line[-1].rfind(';')]
                api_name = pre_name + field
                apis[api_name].append({'name': api_name, 'params': ''})

    def param_type_deal(self, param: str):
        if '@' in param:
            return ''
        for index in StringUtils.find_char(param, '['):
            param = StringUtils.replace_char(param, index, '-')
        for index in StringUtils.find_char(param, ']'):
            param = StringUtils.replace_char(param, index, '')
        for index in StringUtils.find_char(param, '>'):
            param = StringUtils.replace_char(param, index, '')
        if '<' in param:
            return self.param_type_deal(param.split('<')[0]) + '-' + self.param_type_deal(param.split('<')[1])
        if ',' in param:
            return self.param_type_deal(param.split(',')[0]) + '-' + self.param_type_deal(param.split(',')[1])
        if 'java.' in param:
            # param = StringUtils.replace_str(param, 0, param.rfind('<'), param[0: param.rfind('<')].split('.')[-1].split('.')[-1])
            return param.split('.')[-1]
        return param

    def fetch_param(self, api: str):
        params = []
        for param in api.split(', '):
            if self.param_type_deal(param.split(' ')[-1]) != '':
                params.append(self.param_type_deal(param.split(' ')[-1]))
        return params


if __name__ == '__main__':
    a = defaultdict(list)
    print(SDKApi('D:\\Honor\\source_code\\LineageOS\\base\\api\\current.txt',
                 'D:\\Honor\\source_code\\LineageOS').get_api_from_line(a,
                                                                        [], '  public static interface Parcelable.ClassLoaderCreator<T> extends android.os.Parcelable.Creator<T> {'))
