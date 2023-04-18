import re
from typing import Tuple
import time

MoveRenameMethodFormat = "Move And Rename Method (.*) " \
                         "from class (.*) " \
                         "to (.*) " \
                         "from class (.*)"

MoveMethodFormat = "Move Method (.*) " \
                   "from class (.*) " \
                   "to (.*) " \
                   "from class (.*)"

RenameMethodFormat = "Rename Method (.*) " \
                     "renamed to (.*) " \
                     "in class (.*)"

ExtractMethodFormat = "Extract Method (.*) " \
                      "extracted from (.*) " \
                      "in class (.*)"

ExtractMoveMethodFormat = "Extract And Move Method (.*) " \
                          "extracted from (.*) " \
                          "in class (.*) " \
                          "& moved to class (.*)"

RenamePattern = Tuple[re.Pattern, int, int, int, int]

MRMPattern = re.compile(MoveRenameMethodFormat)
MMPattern = re.compile(MoveMethodFormat)
RMPattern = re.compile(RenameMethodFormat)
EMPattern = re.compile(ExtractMethodFormat)
EMMPattern = re.compile(ExtractMoveMethodFormat)

MoveMethodPatterns = [
    (RMPattern, 2, 3, 1, 3),
    (EMPattern, 2, 3, 1, 3),
    (MMPattern, 1, 2, 3, 4),
    (MRMPattern, 1, 2, 3, 4),
    (EMMPattern, 2, 3, 1, 4),
]

RenameClassFormat = "Rename Class (.*) " \
                    "renamed to (.*)"

MoveClassFormat = "Move Class (.*) " \
                  "moved to (.*)"

MoveRenameClassFormat = "Move And Rename Class (.*) " \
                        "moved and renamed to (.*)"

RCPattern = re.compile(RenameClassFormat)
MRCPattern = re.compile(MoveRenameClassFormat)
MCPattern = re.compile(MoveClassFormat)

MoveClassPatterns = [RCPattern, MRCPattern, MCPattern]

RenameParameterFormat = "Rename Parameter (.*) to (.*) " \
                        "in method (.*) " \
                        "from class (.*)"
RPPattern = re.compile(RenameParameterFormat)

AddParameterFormat = "Add Parameter (.*) " \
                     "in method (.*) " \
                     "from class (.*)"
APPattern = re.compile(AddParameterFormat)

RemoveParameterFormat = "Remove Parameter (.*) " \
                        "in method (.*) " \
                        "from class (.*)"

RmPPattern = re.compile(RemoveParameterFormat)

MoveAttributeFormat = "Move Attribute " \
                      "(.*) " \
                      "from class (.*) " \
                      "to (.*) " \
                      "from class (.*)"
MAPattern = re.compile(MoveAttributeFormat)

MoveRenameAttributeFormat = "Move And Rename Attribute " \
                            "(.*)" \
                            " renamed to " \
                            "(.*) " \
                            "and moved from class (.*) " \
                            "to class (.*)"
MRAPattern = re.compile(MoveRenameAttributeFormat)

PushUpAttributeFormat = "Pull Up Attribute " \
                        "(.*) " \
                        "from class (.*) " \
                        "to (.*) " \
                        "from class (.*)"

PUAPattern = re.compile(PushUpAttributeFormat)

RenameAttributeFormat = "Rename Attribute (.*) " \
                        "to (.*) " \
                        "in (.*)"
RAPattern = re.compile(RenameAttributeFormat)

MoveAttributePattern = [(MAPattern, 1, 2, 3, 4),
                        (MRAPattern, 1, 2, 3, 4),
                        (PUAPattern, 1, 2, 3, 4),
                        (RAPattern, 1, 2, 3, 3)]
SignatureFormat = "(private|public|package|protected) (.*)\\((.*)\\)"
SignaturePattern = re.compile(SignatureFormat)

ParamSignatureFormat = "(.*) : (.*)"
ParamSignaturePattern = re.compile(ParamSignatureFormat)


def get_rename_method(sig: str) -> str:
    matched = RMPattern.match(sig)
    if matched:
        source_name = matched.group(1)
        print(source_name)
        return source_name
    else:
        assert False


def get_rename_class(sig: str) -> str:
    matched = RCPattern.match(sig)
    if matched:
        source_name = matched.group(1)
        print(source_name)
        return source_name
    else:
        assert False


def get_name_from_sig(sig: str) -> str:
    matched = SignaturePattern.match(sig)
    if matched:
        method_name = matched.group(2)
        return method_name
    else:
        print('get rename error')
        assert False


def get_param_from_sig(sig: str):
    matched = SignaturePattern.match(sig)
    if matched:
        method_params = matched.group(3)
        if method_params == "":
            return "", ""
        params = method_params.split(", ")
        param_types = []
        param_names = []
        for param in params:
            param_names.append(param.split(' ')[0])
            param_types.append(param.split(' ')[1])
        return " ".join(param_types), " ".join(param_names)
    else:
        print('get params error')
        assert False


def get_param_from_param_sig(sig: str):
    matched = ParamSignaturePattern.match(sig)
    if matched:
        param_type = matched.group(2)
        param_name = matched.group(1)
        return param_type, param_name
    else:
        return '', ''


if __name__ == '__main__':
    test = "public authenticateForOperation(cancel CancellationSignal, executor Executor, callback AuthenticationCallback, operationId long) : long"
    print(get_name_from_sig(test))
    print(get_param_from_sig(test)[1] == '')


def get_method_sig_from_code_elements(code_elements):
    for ce in code_elements:
        if ce["codeElementType"] == "METHOD_DECLARATION":
            return ce["codeElement"]
    assert False


def get_variable_sig_from_code_elements(code_elements):
    for ce in code_elements:
        if ce["codeElementType"] == "SINGLE_VARIABLE_DECLARATION":
            return ce["codeElement"]
    assert False


def get_rename_parameter(refactor_obj):
    description = refactor_obj["description"]
    matched = RPPattern.match(description)
    if matched:
        from_param = matched.group(1)
        to_param = matched.group(2)
        to_method = matched.group(3)
        to_class = matched.group(4)
        from_method = get_method_sig_from_code_elements(refactor_obj["leftSideLocations"])
        from_class = to_class
        return from_param, from_method, from_class, to_param, to_method, to_class
    return None


def get_add_parameter(refactor_obj):
    description = refactor_obj["description"]
    matched = APPattern.match(description)
    if matched:
        to_class = matched.group(3)
        to_method = get_method_sig_from_code_elements(refactor_obj["rightSideLocations"])
        to_param = get_variable_sig_from_code_elements(refactor_obj["rightSideLocations"])
        from_param = 'null'
        from_method = get_method_sig_from_code_elements(refactor_obj["leftSideLocations"])
        from_class = to_class
        return from_param, from_method, from_class, to_param, to_method, to_class
    return None


def get_remove_parameter(refactor_obj):
    description = refactor_obj["description"]
    matched = RmPPattern.match(description)
    if matched:
        to_class = matched.group(3)
        from_class = to_class
        from_method = get_method_sig_from_code_elements(refactor_obj["leftSideLocations"])
        to_method = get_method_sig_from_code_elements(refactor_obj["rightSideLocations"])
        from_param = get_method_sig_from_code_elements(refactor_obj["leftSideLocations"])
        to_param = 'null'
        return from_param, from_method, from_class, to_param, to_method, to_class
    return None


SpecialMoveMethodGetters = [get_add_parameter, get_rename_parameter, get_remove_parameter]

ClassNameFormat = "(.*) class (.*)"
ClassNamePattern = re.compile(ClassNameFormat)
