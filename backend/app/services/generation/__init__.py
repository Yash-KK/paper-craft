from app.services.generation.next_version import (
    generate_next_version_paper,
    run_next_version_generation,
)
from app.services.generation.papers import (
    cancel_version_generation,
    enqueue_new_version,
    enqueue_paper_generation,
    get_paper_detail,
    get_version_detail,
    run_paper_generation,
)
from app.services.generation.service import generate_paper

__all__ = [
    "cancel_version_generation",
    "enqueue_new_version",
    "enqueue_paper_generation",
    "generate_next_version_paper",
    "generate_paper",
    "get_paper_detail",
    "get_version_detail",
    "run_next_version_generation",
    "run_paper_generation",
]
