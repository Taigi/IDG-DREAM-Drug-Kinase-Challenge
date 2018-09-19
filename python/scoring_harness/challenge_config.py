"""
config for drug target challenge.
"""
import pandas as pd
import os
import sys
import evaluation_metrics as eval

CHALLENGE_SYN_ID = "syn15667962"
CHALLENGE_NAME = "IDG-DREAM Drug-Kinase Binding Prediction Challenge"
ADMIN_USER_IDS = [3360851]

REQUIRED_COLUMNS = [
    "Compound_SMILES", "Compound_InchiKeys", "Compound_Name", "UniProt_Id",
    "Entrez_Gene_Symbol", "DiscoveRx_Gene_Symbol", "pKd_[M]_pred"]

CONFIG_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))


def validate_func(submission, goldstandard_path):
    sub_df = pd.read_csv(submission.filePath)
    gs_df = pd.read_csv(goldstandard_path)

    for col in REQUIRED_COLUMNS:
        assert col in sub_df.columns, (
            "Submission file is missing column: " + col)

    assert sub_df.shape[0] == gs_df.shape[0], (
        "Submission file should have " +
        str(gs_df.shape[0]) +
        " predictions")

    combined_df = pd.merge(sub_df, gs_df, how='inner')

    assert combined_df.shape[0] == gs_df.shape[0], (
        "After merging submission file and gold standard, resulting table is" +
        "missing predictions")
    return(True, "Passed Validation")


def score1(submission, goldstandard_path):
    sub_df = pd.read_csv(submission.filePath)
    gs_df = pd.read_csv(goldstandard_path)
    combined_df = pd.merge(sub_df, gs_df, how='inner')
    actual = combined_df["pKd_[M]"]
    predicted = combined_df["pKd_[M]_pred"]
    rmse = round(eval.rmse(actual, predicted), 4)
    pearson = round(eval.pearson(actual, predicted), 4)
    spearman = round(eval.spearman(actual, predicted), 4)
    ci = round(eval.ci(actual, predicted), 4)
    f1 = round(eval.f1(actual, predicted), 4)
    average_AUC = round(eval.average_AUC(actual, predicted), 4)
    return(rmse, pearson, spearman, ci, f1, average_AUC)


evaluation_queues = [
    {
        'id': 9614078,
        'scoring_func': score1,
        'validation_func': validate_func,
        'goldstandard_path': CONFIG_DIR + "/round_1_test_data.csv"
    },
    {
        'id': 9614079,
        'scoring_func': score1,
        'validation_func': validate_func,
        'goldstandard_path': CONFIG_DIR + "/round_2_test_data.csv"

    }
]
evaluation_queue_by_id = {q['id']:q for q in evaluation_queues}


## define the default set of columns that will make up the leaderboard
LEADERBOARD_COLUMNS = [
    dict(name='objectId',      display_name='ID',      columnType='STRING', maximumSize=20),
    dict(name='userId',        display_name='User',    columnType='STRING', maximumSize=20, renderer='userid'),
    dict(name='entityId',      display_name='Entity',  columnType='STRING', maximumSize=20, renderer='synapseid'),
    dict(name='versionNumber', display_name='Version', columnType='INTEGER'),
    dict(name='name',          display_name='Name',    columnType='STRING', maximumSize=240),
    dict(name='team',          display_name='Team',    columnType='STRING', maximumSize=240)]

## Here we're adding columns for the output of our scoring functions, score,
## rmse and auc to the basic leaderboard information. In general, different
## questions would typically have different scoring metrics.
leaderboard_columns = {}
for q in evaluation_queues:
    leaderboard_columns[q['id']] = LEADERBOARD_COLUMNS + [
        dict(name='score',         display_name='Score',   columnType='DOUBLE'),
        dict(name='rmse',          display_name='RMSE',    columnType='DOUBLE'),
        dict(name='auc',           display_name='AUC',     columnType='DOUBLE')]

## map each evaluation queues to the synapse ID of a table object
## where the table holds a leaderboard for that question
leaderboard_tables = {}


def validate_submission(evaluation, submission):
    """
    Find the right validation function and validate the submission.

    :returns: (True, message) if validated, (False, message) if
              validation fails or throws exception
    """
    config = evaluation_queue_by_id[int(evaluation.id)]
    validated, validation_message = config['validation_func'](submission, config['goldstandard_path'])

    return True, validation_message


def score_submission(evaluation, submission):
    """
    Find the right scoring function and score the submission

    :returns: (score, message) where score is a dict of stats and message
              is text for display to user
    """
    config = evaluation_queue_by_id[int(evaluation.id)]
    score = config['scoring_func'](submission, config['goldstandard_path'])
    return (dict(
        rmse=score[0],
        pearson=score[1],
        spearman=score[2],
        ci=score[3],
        f1=score[4],
        average_AUC=score[5]),
            "You did fine!")