from app.services.generation.papers import (
    enqueue_new_version,
    enqueue_paper_generation,
    get_paper_detail,
    get_version_detail,
    run_paper_generation,
)
from app.services.generation.next_version import (
    generate_next_version_paper,
    run_next_version_generation,
)
from app.services.generation.service import generate_paper

__all__ = [
    "enqueue_new_version",
    "enqueue_paper_generation",
    "generate_paper",
    "generate_next_version_paper",
    "get_paper_detail",
    "get_version_detail",
    "run_paper_generation",
    "run_next_version_generation",
]
