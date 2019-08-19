import logging
from scaffold.structured_log import StructuredMessage as m
from scaffold.operations import find_files_with_text, find_files


def evaluate_condition(conditions: list, root_path: str) -> bool:
    evaluated_conditions = []
    nested_conditions = [c for c in conditions if 'operator' in c]
    for c in nested_conditions:
        conditions_result = evaluate_condition(c['conditions'], root_path)
        evaluated_conditions.append(conditions_result)
    other_conditions = [c for c in conditions if 'operator' not in c]
    for c in other_conditions:
        if c['type'] == 'FIND_IN_FILES':
            logging.info(m('evaluating condition for find in files', condition=c))
            try:
                files = find_files_with_text(root_path, c['findInFiles'], c['findText'])
                evaluated_conditions.append(len(files) > 0)
            except BaseException as ex:
                logging.error(m('encountered error finding in files', error=ex))
                evaluated_conditions.append(False)
        elif c['type'] == 'FIND_FILES':
            logging.info(m('evaluating condition for finding files', condition=c))
            try:
                files = find_files(root_path, c['filePatterns'])
                evaluated_conditions.append(len(files) > 0)
            except BaseException as ex:
                logging.error(m('encountered error finding files', error=ex))
                evaluated_conditions.append(False)
        else:
            raise ValueError('unexpected condition type')
    if c['operator'] == 'AND':
        if c['inverse']:
            return any([c for c in evaluated_conditions if c])
        else:
            return any([c for c in evaluated_conditions if not c])
    elif c['operator'] == 'OR':
        if c['inverse']:
            return any([c for c in evaluated_conditions if not c])
        else:
            return any([c for c in evaluated_conditions if c])
    else:
        raise ValueError('expected operator to be "AND" or "OR"')
