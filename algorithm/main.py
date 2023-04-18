import argparse
from algorithm.utils import FileJson, FileCSV, Constant
from algorithm.model.build_model import BuildModel
# from algorithm.model.anti_pattern import AntiPattern
# from algorithm.model.coupling_pattern import CouplingPattern
from algorithm.model.patterns.coupling_patterns import CouplingPattern
from algorithm.model.match import Match
from algorithm.model.git_history import GitHistory
from algorithm.model.mc.mc import MC

access_map = {'': '0', 'Private': '1', 'Protected': '2', 'Public': '3'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--code_honor', '-re', action='store', dest='code_honor',
                        help='code path of honor')
    parser.add_argument('--code_android', '-ra', action='store', dest='code_android',
                        help='code path of android')
    parser.add_argument('--honor', '-e', action='store', dest='honor',
                        help='root json file of honor')
    parser.add_argument('--android', '-a', action='store', dest='android',
                        help='root json file of android')
    parser.add_argument('--refactor_miner', '-ref', action='store', dest='refactor_miner',
                        help='root directory of refactor miner tool')
    parser.add_argument('--output', '-o', action='store', dest='output',
                        help='root directory of out')
    args = parser.parse_args()
    dispatch(args)


def dispatch(args):
    if not hasattr(args, 'honor'):
        raise ValueError("root directory of project must supply")
    if args.code_honor is None:
        raise ValueError("root directory of project must supply")
    if args.code_android is None:
        raise ValueError("root directory of project must supply")
    if args.honor is None:
        raise ValueError("root directory of project must supply")
    if args.android is None:
        raise ValueError("root directory of project must supply")
    if args.output is None:
        raise ValueError("root directory of project must supply")
    # read files
    try:
        entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp, entities_stat_aosp = \
            FileJson.read_from_json(args.android, args.honor)
        # 读取模块责任田
        module_blame = args.output

        # build base model
        git_history = GitHistory(args.code_android, args.code_honor, args.honor, args.refactor_miner,
                                 args.output)

        base_model = BuildModel(entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp,
                                entities_stat_aosp, git_history, args.output)

        mc = MC(args.output, args.code_honor, list(base_model.file_set_extension), args.code_android,
                list(base_model.file_set_android))
        mc.get_mc()

        pattern_match = Match(base_model, args.output, module_blame, args.code_honor)
        # match coupling pattern
        coupling_pattern = CouplingPattern()
        pattern_match.start_match_pattern(coupling_pattern)

        # match anti pattern
        # special_anti_pattern = AntiPattern()
        # pattern_match.start_match_pattern(special_anti_pattern)
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
