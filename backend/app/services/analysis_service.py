"""Analysis service stub.

Will eventually implement: tokenisation → normalisation → winnowing → scoring.
For now the worker calls this and it returns immediately (no-op).
"""
from pymongo.database import Database


def run_analysis_for_assignment(
    db: Database, assignment_id: str, run_id: str
) -> None:
    """Run the similarity-analysis pipeline for one assignment.

    TODO: iterate submissions, read merged files, tokenise, fingerprint,
          compute pairwise similarity, and write SimilarityResult docs.
    """
    pass
