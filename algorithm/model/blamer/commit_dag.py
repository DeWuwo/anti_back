from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Set, Generator

import git

SHA = str


def look_up_parent_commit(repo: git.Repo, sha: SHA) -> SHA:
    ...


class CommitNode:
    sha: str
    parent_commits: Set[SHA]
    target_commits: Set[SHA]

    def __init__(self, sha: SHA):
        self.sha = sha
        self.parent_commits = set()
        self.target_commits = set()


class CommitDAG:
    repo: git.Repo
    node_dict: Dict[SHA, CommitNode]

    def __init__(self, repo: git.Repo):
        self.repo = repo
        self.node_dict = dict()
        self.build_commit_graph(repo)

    def build_commit_graph(self, repo: git.Repo):
        def create_if_not_exists(sha: SHA):
            if sha not in self.node_dict:
                new_commit_node = CommitNode(sha)
                self.node_dict[sha] = new_commit_node
                return new_commit_node
            else:
                return self.node_dict[sha]

        for commit in repo.iter_commits(rev='master'):
            commit_sha = commit.__str__()
            commit_node = create_if_not_exists(commit_sha)
            for parent_commit in commit.parents:
                parent_commit_node = create_if_not_exists(parent_commit.__str__())
                parent_commit_node.target_commits.add(commit_node.sha)
                commit_node.parent_commits.add(parent_commit_node.sha)


def commit_dag_generator(commit_dag: CommitDAG, sha: SHA) -> Generator[CommitNode, None, None]:
    def build_degree_set(start_commit: CommitNode):
        bfa_queue = [start_commit]
        visited_helper_set: Set[SHA] = set()
        while bfa_queue:
            current_node = bfa_queue.pop(0)
            if current_node.sha in visited_helper_set:
                continue
            else:
                visited_helper_set.add(current_node.sha)
            for sha1 in current_node.target_commits:
                degree_dict[sha1] += 1
                bfa_queue.append(commit_dag.node_dict[sha1])

    commit_node = commit_dag.node_dict[sha]

    visited_set: Set[SHA] = set()
    visited_set.add(commit_node.sha)
    visiting_queue = [commit_node]
    degree_dict: Dict[SHA, int] = defaultdict(int)
    build_degree_set(commit_node)
    while visiting_queue:
        node = visiting_queue.pop()
        yield node
        for target_sha in node.target_commits:
            degree_dict[target_sha] -= 1
            if degree_dict[target_sha] == 0:
                visiting_queue.append(commit_dag.node_dict[target_sha])


if __name__ == "__main__":
    base_repo_path = Path("D:\\Master\\CodeSmell\\Refactor\\frameworks\\base")
    commit_graph = CommitDAG(git.Repo(base_repo_path))
    generator = commit_dag_generator(commit_graph, "fa270050cb9b257beb5d3645376b9ad6bccaea6c")
    s = set()
    for commit_node in generator:
        assert commit_node.sha not in s
        s.add(commit_node.sha)
        print(commit_node)
    print()
