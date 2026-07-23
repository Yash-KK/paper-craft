from app.db.models.chapter_catalog import ChapterCatalog
from app.db.models.notebook import Board, ClassGrade, Subject
from app.db.session import SyncSessionLocal

CLASS_10_MATH_CHAPTERS = [
    {"chapter_number": 1, "chapter_name": "Real Numbers", "book_code": "jemh1", "source_file": "jemh101.md"},
    {"chapter_number": 2, "chapter_name": "Polynomials", "book_code": "jemh1", "source_file": "jemh102.md"},
    {"chapter_number": 3, "chapter_name": "Pair of Linear Equations in Two Variables", "book_code": "jemh1", "source_file": "jemh103.md"},
    {"chapter_number": 4, "chapter_name": "Quadratic Equations", "book_code": "jemh1", "source_file": "jemh104.md"},
    {"chapter_number": 5, "chapter_name": "Arithmetic Progressions", "book_code": "jemh1", "source_file": "jemh105.md"},
    {"chapter_number": 6, "chapter_name": "Triangles", "book_code": "jemh1", "source_file": "jemh106.md"},
    {"chapter_number": 7, "chapter_name": "Coordinate Geometry", "book_code": "jemh1", "source_file": "jemh107.md"},
    {"chapter_number": 8, "chapter_name": "Introduction to Trigonometry", "book_code": "jemh1", "source_file": "jemh108.md"},
    {"chapter_number": 9, "chapter_name": "Some Applications of Trigonometry", "book_code": "jemh1", "source_file": "jemh109.md"},
    {"chapter_number": 10, "chapter_name": "Circles", "book_code": "jemh1", "source_file": "jemh110.md"},
    {"chapter_number": 11, "chapter_name": "Areas Related to Circles", "book_code": "jemh1", "source_file": "jemh111.md"},
    {"chapter_number": 12, "chapter_name": "Surface Areas and Volumes", "book_code": "jemh1", "source_file": "jemh112.md"},
    {"chapter_number": 13, "chapter_name": "Statistics", "book_code": "jemh1", "source_file": "jemh113.md"},
    {"chapter_number": 14, "chapter_name": "Probability", "book_code": "jemh1", "source_file": "jemh114.md"},
]


def seed_chapters() -> None:
    db = SyncSessionLocal()
    try:
        print("Checking for existing chapters to prevent duplicates...")

        for chapter in CLASS_10_MATH_CHAPTERS:
            existing = (
                db.query(ChapterCatalog)
                .filter(
                    ChapterCatalog.board == Board.CBSE,
                    ChapterCatalog.book_code == chapter["book_code"],
                    ChapterCatalog.chapter_number == chapter["chapter_number"],
                )
                .first()
            )

            if not existing:
                new_chapter = ChapterCatalog(
                    board=Board.CBSE,
                    book_code=chapter["book_code"],
                    subject=Subject.MATHEMATICS,
                    grade=ClassGrade.CLASS_10,
                    chapter_number=chapter["chapter_number"],
                    chapter_name=chapter["chapter_name"],
                    source_file=chapter["source_file"],
                )
                db.add(new_chapter)
                print(
                    f"Added: Chapter {chapter['chapter_number']} - {chapter['chapter_name']}"
                )
            else:
                print(
                    f"Skipped (already exists): Chapter {chapter['chapter_number']} - {chapter['chapter_name']}"
                )

        db.commit()
        print("\nSeeding complete!")

    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_chapters()
