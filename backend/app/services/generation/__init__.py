from app.services.generation.papers import (
    create_and_generate_paper,
    get_paper_detail,
)
from app.services.generation.service import generate_paper

__all__ = [
    "create_and_generate_paper",
    "generate_paper",
    "get_paper_detail",
]
