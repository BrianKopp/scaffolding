from typing import List
import logging
import subprocess
from git import Repo
import os
from scaffold.conditions import evaluate_condition
from scaffold.structured_log import StructuredMessage as m
import scaffold.operations as scops


def execute_job(job_id: str, github_org: str, git_environments: List[str],
                operatons: list, root_path) -> bool:
    repo_branches = get_repos_and_branches(git_environments)
    for repo_name in repo_branches:
        logging.info('cloning {}'.format(repo_name))
        for branch in repo_branches[repo_name]:
            branch_path = os.path.join(root_path, repo_name, branch)
            perform_branch_activities(job_id, branch_path, repo_name, branch, operations)
    return


def get_repos_and_branches(git_environments: List[str]):
    repo_branches = {}
    try:
        for git_env in git_environments:
            parts = git_env.split('/')
            if parts[0] in repo_branches:
                repo_branches[parts[0]].append(parts[1])
            else:
                repo_branches[parts[0]] = [parts[1]]
        return repo_branches
    except BaseException as ex:
        logging.error('error parsing git_environments', ex, git_environments)
        return {}


def perform_branch_activities(job_id: str, branch_path: str,
                              repo_name: str, branch: str,
                              commit_message: str, pull_request_name: str,
                              operations: list):
    repo = Repo.clone_from(
        'https://github.com/{}/{}'.format(github_org, repo_name),
        branch_path,
        branch=branch
    )

    messages = []
    affected_files = []

    new_branch = repo.create_head('{branch}-{job_id}')
    new_branch.checkout()

    for op in operations:
        if 'conditions' in op and not evaluate_condition(conditions, branch_path):
            continue
        if op['type'] == 'FIND_AND_REPLACE_IN_FILES':
            result = scops.find_and_replace(
                branch_path,
                op['findInFiles'],
                op['findText'],
                op['replaceText']
            )
            affected_files.extend(result)
            messages.append(create_message(
                op,
                len(result) > 0),
                'found and replaced text in {} files: {}'.format(len(result), ','.join(result))
            )
        elif op['type'] == 'FIND_IN_FILES':
            result = scops.find_files_with_text(
                branch_path,
                op['findInFiles'],
                op['findText']
            )
            messages.append(create_message(
                op,
                len(result) > 0,
                'found {} files with search text in them. files: {}'.format(len(result), ','.join(result))
            ))
        elif op['type'] == 'FIND_FILES':
            result = scops.find_files(
                branch_path,
                op['filePatterns']
            )
            messages.append(create_message(
                op,
                len(result) > 0,
                'found {} files matching pattern(s). files: {}'.format(len(results), ','.join(result))
            ))
        elif op['type'] == 'ADD_FILE':
            try:
                scops.create_file(
                    branch_path,
                    op['fileName'],
                    op['fileContents']
                )
                result = True
            except BaseException as ex:
                logging.error('error adding file', ex)
                result = False
            affected_files.extend(op['fileName'])
            messages.append(create_message(
                op,
                result,
                None if result else ex
            ))
        elif op['type'] == 'DELETE_FILES':
            for f in op['fileNames']:
                try:
                    scops.delete_file(branch_path, f)
                    affected_files.append(f)
                except BaseException as ex:
                    logging.error('error deleting file {}'.format(f), ex)
                    messages.append(create_message(op, False, 'error deleting file {}'.format(f)))
                    continue
            messages.append(create_message(op, True))
        else:
            raise ValueError('unexpected operation type {}'.format(op['type']))
    
    new_branch.index.add(affected_files)
    new_branch.index.commit(commit_message)
    repo.remotes.origin.push()
    return


def create_message(operation, result, extra_msg = None):
    which_report_action = 'successReportAction' if result else 'failureReportAction'
    return (operation[which_report_action][severity], operation[which_report_action][message], extra_msg)
