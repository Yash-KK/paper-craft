"""Back-compat shim — prefer ``app.services.export``.

This module used to own the DOCX builder. The implementation now lives in
``app.services.export``. Notebooks can keep importing from here.
"""

from app.services.export import (  # noqa: F401
    build_answer_key_docx,
    build_question_paper_docx,
    export_question_paper_and_answer_key,
    export_question_paper_only,
)
