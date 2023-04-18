import re
import os
import csv
import glob
from collections import defaultdict
from functools import partial

from algorithm.model.mc.basedata import ModifyDetail
from algorithm.model.mc.basedata import CommitDetail
from algorithm.utils import FileCSV


class MC:
    code_path: str
    out_path: str
    file_list: list
    code_path_nat: str
    file_list_nat: list

    def __init__(self, out_path, code_path, file_list, code_path_nat, file_list_nat):
        self.out_path = out_path
        self.code_path = code_path
        self.file_list = file_list
        self.code_path_nat = code_path_nat
        self.file_list_nat = file_list_nat

    def process_git_log(self, fileName, fileList_java):
        print('  process git log')
        commitCollection_java = list()

        commitId = ""
        authorName = ""
        date = ""
        fileList = list()
        delList = list()
        addList = list()
        issueIds = list()
        fp = open(fileName, encoding="utf8", errors='ignore')
        num = 0
        for line in fp:
            num += 1
            # print(num)
            if re.match(r"commit\s[0-9a-zA-Z]+", line):
                if (commitId != ""):
                    # print("process ", commitId, authorName, date, fileList, addList, delList, issueIds)
                    [isKept, oneCommit] = self.processPreCmt(commitId, authorName, date, fileList, addList, delList,
                                                             issueIds, fileList_java)
                    if isKept:
                        commitCollection_java.append(oneCommit)

                    # print("clear", print (len(commitCollection)))
                    # clear
                    fileList = list()
                    delList = list()
                    addList = list()
                    issueIds = list()

                match = re.match(r"commit\s[0-9a-zA-Z]+", line)
                commitId = match.group().split("commit ")[1]

            elif re.match(r"Author: ", line):
                strList = line.split("Author: ")[1].split("<")
                authorName = strList[0].strip()
                authorEmail = strList[1].split(">")[0]

            elif re.match(r"Date:   ", line):
                date = line.split("Date:   ")[1].strip("\n")

            elif re.match(r"[0-9]+	[0-9]+	", line):
                strList = line.strip("\n").split("	")
                addLoc = int(strList[0])
                delLoc = int(strList[1])
                fileName = strList[2]
                fileList.append(fileName)
                addList.append(addLoc)
                delList.append(delLoc)
            elif re.findall(r"Bug: [0-9]+", line):
                match = re.findall(r"Bug: [0-9]+", line)
                for issueId in match:
                    issueIds.append(int(issueId.split("Bug: ")[1]))
            # end if
        # end for
        [isKept, oneCommit] = self.processPreCmt(commitId, authorName, date, fileList, addList, delList, issueIds,
                                                 fileList_java)
        if isKept:
            commitCollection_java.append(oneCommit)

        fp.close()
        return commitCollection_java

    def processGitLog(self, fileName, fileList_all, fileList_py, fileList_notest):
        print('  process git log')
        commitCollection_all = list()
        commitCollection_py = list()
        commitCollection_notest = list()

        commitId = ""
        authorName = ""
        date = ""
        fileList = list()
        delList = list()
        addList = list()
        issueIds = list()
        fp = open(fileName, encoding="utf8", errors='ignore')
        num = 0
        for line in fp:
            num += 1
            # print(num)
            if re.match(r"commit\s[0-9a-zA-Z]+", line):
                if (commitId != ""):
                    # print("process ", commitId, authorName, date, fileList, addList, delList, issueIds)
                    [isKept, oneCommit] = self.processPreCmt(commitId, authorName, date, fileList, addList, delList,
                                                             issueIds, fileList_all)
                    if isKept:
                        commitCollection_all.append(oneCommit)
                    [isKept, oneCommit] = self.processPreCmt(commitId, authorName, date, fileList, addList, delList,
                                                             issueIds, fileList_py)
                    if isKept:
                        commitCollection_py.append(oneCommit)
                    [isKept, oneCommit] = self.processPreCmt(commitId, authorName, date, fileList, addList, delList,
                                                             issueIds, fileList_notest)
                    if isKept:
                        commitCollection_notest.append(oneCommit)

                    # print("clear", print (len(commitCollection)))
                    # clear
                    fileList = list()
                    delList = list()
                    addList = list()
                    issueIds = list()

                match = re.match(r"commit\s[0-9a-zA-Z]+", line)
                commitId = match.group().split("commit ")[1]

            elif re.match(r"Author: ", line):
                strList = line.split("Author: ")[1].split("<")
                authorName = strList[0].strip()
                authorEmail = strList[1].split(">")[0]

            elif re.match(r"Date:   ", line):
                date = line.split("Date:   ")[1].strip("\n")

            elif re.match(r"[0-9]+	[0-9]+	", line):
                strList = line.strip("\n").split("	")
                addLoc = int(strList[0])
                delLoc = int(strList[1])
                fileName = strList[2]
                fileList.append(fileName)
                addList.append(addLoc)
                delList.append(delLoc)
            elif re.findall(r"Bug: [0-9]+", line):
                match = re.findall(r"Bug: [0-9]+", line)
                for issueId in match:
                    issueIds.append(int(issueId.split("Bug: ")[1]))
            # end if
        # end for
        [isKept, oneCommit] = self.processPreCmt(commitId, authorName, date, fileList, addList, delList, issueIds,
                                                 fileList_all)
        if isKept:
            commitCollection_all.append(oneCommit)
        [isKept, oneCommit] = self.processPreCmt(commitId, authorName, date, fileList, addList, delList, issueIds,
                                                 fileList_py)
        if isKept:
            commitCollection_py.append(oneCommit)
        [isKept, oneCommit] = self.processPreCmt(commitId, authorName, date, fileList, addList, delList, issueIds,
                                                 fileList_notest)
        if isKept:
            commitCollection_notest.append(oneCommit)

        fp.close()
        return commitCollection_all, commitCollection_py, commitCollection_notest

    def processPreCmt(self, commitId, authorName, date, fileList, addList, delList, issueIds, filterList):
        # filter fileList, addList, delList
        newFileList = list()
        newDelList = list()
        newAddList = list()
        for index in range(0, len(fileList)):
            if fileList[index] in filterList:  # should be kept
                newFileList.append(fileList[index])
                newDelList.append(delList[index])
                newAddList.append(addList[index])

        # save
        if len(newFileList) == 0:
            isKept = False
        else:
            isKept = True
        modifyDetail = ModifyDetail(newFileList, newAddList, newDelList)
        oneCommit = CommitDetail(commitId, authorName, date, issueIds, modifyDetail)
        return isKept, oneCommit

    def getAllFilesByFilter(self):
        print('   get all files by filter')
        # srcName = projectName.split("-no-test")[0]
        # dir = projectName + "\\"
        # dir = "C:\\Users\\wj86\\Documents\\gitrepo\\python-workspace\\project-no-test\\" + projectName + "\\"

        fileList_all = list()
        fileList_py = list()
        fileList_notest = list()
        for filename in glob.iglob(self.code_path + '\\**\\*', recursive=True):
            filename = filename.split(self.code_path + '\\')[1]
            filename = filename.replace("\\", "/")
            if (filename.startswith(".git") or filename.startswith(".github")):
                continue
            # print(filename)

            fileList_all.append(filename)
            if (filename.endswith(".java")):
                fileList_py.append(filename)
                if "tests/" not in filename and "test/" not in filename and "test_" not in filename and "_test.py" not in filename:
                    fileList_notest.append(filename)

        print("file benchmark: ", len(fileList_all), len(fileList_py), len(fileList_notest))
        return fileList_all, fileList_py, fileList_notest

    def run_log_fetch(self, proj, filelist_java):
        print('fetch git log')
        # gitlogFile = generateLog(projectName)
        if os.path.exists(f"{self.out_path}/mc/history-java_{proj}.csv"):
            return

        commitCollection_java = self.process_git_log(os.path.join(self.out_path, f'mc/gitlog_{proj}'), filelist_java)

        # [fileList_all, fileList_java, fileList_notest] = self.getAllFilesByFilter()
        # [commitCollection_all, commitCollection_java, commitCollection_nontest] = \
        #     self.processGitLog(os.path.join(self.out_path, f'mc/gitlog_{proj}'), fileList_all, fileList_java, fileList_notest)

        # resList = saveCommitCollection(commitCollection_all)
        # fileName = f"{self.out_path}\\mc\\history-all_{proj}.csv"
        # writeCSV(resList, fileName)

        resList = saveCommitCollection(commitCollection_java)
        fileName = f"{self.out_path}\\mc\\history-java_{proj}.csv"
        writeCSV(resList, fileName)

        # resList = saveCommitCollection(commitCollection_nontest)
        # fileName = f"{self.out_path}\\mc\\history-notest_{proj}.csv"
        # writeCSV(resList, fileName)

    # read mc file
    def read_mc_file(self, proj):
        mcAuthorDict = dict()  # [filename][author] = the commit count by this author
        mcCommittimesDict = dict()  # [filename] = cmttimes
        mcChangeLocDict = dict()  # [fileName] = loc
        mcIssueCountDict = dict()  # [fileName][issueId] = issue cmt counts
        mcIssueLocDict = dict()  # [fileName][issueId] = issueloc
        with open(os.path.join(self.out_path, f'mc/history-java_{proj}.csv'), "r", encoding="utf8") as fp:
            reader = csv.reader(fp, delimiter=",")
            for each in reader:
                [commitId, author, date, issueIds, files, addLocs, delLocs] = each
                fileNameList = files.split(";")
                addLocList = addLocs.split(";")
                delLocList = delLocs.split(";")
                if issueIds == "":
                    issueIdList = list()
                else:
                    issueIdList = issueIds.split(";")

                # fileNameList = formatFileName(fileNameList)
                '''
                print("fileNameList", fileNameList)
                print("addLocList", addLocList)
                print("delLocList", delLocList)
                print("issueIdList", issueIdList)
                '''
                # author releated
                for fileName in fileNameList:
                    if fileName not in mcAuthorDict:
                        mcAuthorDict[fileName] = dict()
                    if author not in mcAuthorDict[fileName]:
                        mcAuthorDict[fileName][author] = 1
                    else:
                        mcAuthorDict[fileName][author] += 1

                # commit times related
                for fileName in fileNameList:
                    if fileName not in mcCommittimesDict:
                        mcCommittimesDict[fileName] = 1
                    else:
                        mcCommittimesDict[fileName] += 1

                # LOC changed related
                for index in range(0, len(fileNameList)):
                    fileName = fileNameList[index]
                    loc = int(addLocList[index]) + int(delLocList[index])
                    if fileName not in mcChangeLocDict:
                        mcChangeLocDict[fileName] = loc
                    else:
                        mcChangeLocDict[fileName] += loc

                # issue counts related
                for index in range(0, len(fileNameList)):
                    fileName = fileNameList[index]
                    if fileName not in mcIssueCountDict:
                        mcIssueCountDict[fileName] = dict()
                    for issueId in issueIdList:
                        if issueId not in mcIssueCountDict[fileName]:
                            mcIssueCountDict[fileName][issueId] = 1
                        else:
                            mcIssueCountDict[fileName][issueId] += 1

                # issue loc related
                for index in range(0, len(fileNameList)):
                    fileName = fileNameList[index]
                    loc = int(addLocList[index]) + int(delLocList[index])
                    if fileName not in mcIssueLocDict:
                        mcIssueLocDict[fileName] = dict()
                    for issueId in issueIdList:
                        if issueId not in mcIssueLocDict[fileName]:
                            mcIssueLocDict[fileName][issueId] = loc
                        else:
                            mcIssueLocDict[fileName][issueId] += loc

        return mcAuthorDict, mcCommittimesDict, mcChangeLocDict, mcIssueCountDict, mcIssueLocDict

    '''
    #for one project information, compute the bug,change cost
    #mcAuthorDict = dict()   # [filename][author] = the commit count by this author
    mcCommittimesDict = dict() #[filename] = cmttimes
    mcChangeLocDict = dict()  #[fileName] = loc
    mcIssueCountDict = dict()  #[fileName][issueId] = issue cmt counts
    mcIssueLocDict = dict()  #[fileName][issueId] = issueloc
    fileName_deptype_list=[fileId, filename, dependencytype, dependencytype-count]
    #output is a list of [filename, dependency-type, commit-times, add+del LOC, issue-counts, issue-add-del LOC]
    '''

    def change_bug_proness_compute(self, fileName_list, mcAuthorDict, mcCommittimesDict, mcChangeLocDict,
                                   mcIssueCountDict, mcIssueLocDict):
        res = []
        for index in range(0, len(fileName_list)):
            each = fileName_list[index]
            fileName = each
            authorCount = search_author_count(mcAuthorDict, fileName)
            cmtCount = search_count(mcCommittimesDict, fileName)
            changeLoc = search_count(mcChangeLocDict, fileName)
            [issueCount, issueCmtCount] = search_issue_count(mcIssueCountDict, fileName)
            issueLoc = search_iisue_loc(mcIssueLocDict, fileName)
            res.append([fileName, authorCount, cmtCount, changeLoc, issueCount, issueCmtCount, issueLoc])
        return res

    def get_mc_file(self, proj, filelist_java):
        if os.path.exists(f"{self.out_path}/mc/file-mc_{proj}.csv") and os.path.exists(
                f"{self.out_path}/mc/file-mc_rank_{proj}.csv"):
            return
        self.run_log_fetch(proj, filelist_java)
        print('get file-mc.csv')
        [mcAuthorDict, mcCommittimesDict, mcChangeLocDict, mcIssueCountDict,
         mcIssueLocDict] = self.read_mc_file(proj)  # [filename]=, cmttimes, changeLoc, issueCounts, issueLoc;
        '''
        print("mcAuthorDict", mcAuthorDict)
        print("mcCommittimesDict", mcCommittimesDict)
        print("mcChangeLocDict", mcCommittimesDict)
        print("mcIssueLocDict", mcCommittimesDict)
        print("mcIssueCountDict", mcCommittimesDict)
        '''
        change_bug_cost_list = self.change_bug_proness_compute(filelist_java, mcAuthorDict, mcCommittimesDict,
                                                               mcChangeLocDict, mcIssueCountDict, mcIssueLocDict)
        self.get_mc_rank(change_bug_cost_list, proj)
        title = ['filename', '#author', '#cmt', 'changeloc', '#issue', '#issue-cmt', 'issueLoc']
        final = list()
        final.append(title)
        final.extend(change_bug_cost_list)
        writeCSV(final, os.path.join(self.out_path, f'mc/file-mc_{proj}.csv'))

    def get_mc(self):
        self.get_mc_file('nat', self.file_list_nat)
        self.get_mc_file('ext', self.file_list)

    def get_mc_rank(self, mc_data: list, proj):
        rank = defaultdict(partial(defaultdict, str))
        title = ['filename', '#author', '#cmt', 'changeloc', '#issue', '#issue-cmt', 'issueLoc']
        title_index = [1, 2, 3, 4, 5, 6]
        for key_index in title_index:
            mc_data_copy = mc_data.copy()
            mc_data_copy.sort(key=lambda x: x[key_index], reverse=True)
            file_num = len(mc_data_copy)

            for index in range(0, file_num):
                rank[mc_data_copy[index][0]]['file_count'] = str(file_num)
                rank[mc_data_copy[index][0]][title[0]] = mc_data_copy[index][0]
                rank[mc_data_copy[index][0]][title[key_index]] = index
        FileCSV.write_dict_to_csv(os.path.join(self.out_path, 'mc'), f'file-mc_rank_{proj}',
                                  [value for _, value in rank.items()], 'w')


def formatFileName(fileNameList):
    for index in range(0, len(fileNameList)):
        fileName = fileNameList[index]
        fileName = fileName.replace(".", "_")
        fileName = fileName.replace("/", ".")
        fileNameList[index] = fileName
    return fileNameList


def search_author_count(mcAuthorDict, fileName):
    if fileName in mcAuthorDict:
        return len(list(mcAuthorDict[fileName].keys()))
    else:
        return 0


def search_count(aDict, fileName):
    if fileName in aDict:
        return aDict[fileName]
    else:
        return 0


def search_issue_count(mcIssueCountDict, fileName):
    issueCount = 0
    if fileName in mcIssueCountDict:
        issueCount = len(list(mcIssueCountDict[fileName].keys()))
        issueCmtCount = sum(list(mcIssueCountDict[fileName].values()))
    else:
        issueCount = 0
        issueCmtCount = 0
    return issueCount, issueCmtCount


def search_iisue_loc(mcIssueLocDict, fileName):
    if fileName in mcIssueLocDict:
        loc = sum(list(mcIssueLocDict[fileName].values()))
        return loc
    else:
        return 0


def writeCSV(aList, fileName):
    with open(fileName, "w", newline="", encoding='utf-8') as fp:
        writer = csv.writer(fp, delimiter=",")
        writer.writerows(aList)
    print("commit len: ", len(aList))


def saveCommitCollection(commitCollection):
    resList = list()
    for oneCommit in commitCollection:
        row = oneCommit.toList()
        resList.append(row)
        # print(row)
    return resList
