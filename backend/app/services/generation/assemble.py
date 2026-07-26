def assemble_node(state: dict) -> dict:
    items = sorted(state["generated_items"], key=lambda x: x["question_number"])
    student_paper: dict = {"sections": {}}
    answer_key: dict = {"sections": {}}

    for item in items:
        sec = item["section_name"]
        student_paper["sections"].setdefault(sec, []).append(
            {
                "question_number": item["question_number"],
                "question_type": item["question_type"],
                "question_text": item["question_text"],
                "options": item["options"],
                "marks": item["marks"],
                "sub_parts": item["sub_parts"],
                "alternate_question_text": item["alternate_question_text"],
            }
        )
        answer_key["sections"].setdefault(sec, []).append(
            {
                "question_number": item["question_number"],
                "chapter_name": item["chapter_name"],
                "answer": item["answer"],
                "correct_option": item["correct_option"],
                "marking_rubric": item["marking_rubric"],
                "alternate_answer": item["alternate_answer"],
                "status": item["status"],
            }
        )

    return {"final_paper": student_paper, "final_answer_key": answer_key}
