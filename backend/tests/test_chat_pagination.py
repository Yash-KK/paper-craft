from app.api.v1.chat import ChatMessagePage
from app.repositories.chat import ChatRepository


def test_chat_message_page_defaults_to_five():
    params = ChatMessagePage.__params_type__()
    assert params.size == 5


def test_messages_cursor_query_orders_newest_first():
    repo = ChatRepository(db=None)  # type: ignore[arg-type]
    query = repo.messages_cursor_query(session_id=__import__("uuid").uuid4())
    order_sql = str(query.compile(compile_kwargs={"literal_binds": False}))
    assert "created_at" in order_sql.lower()
    # DESC must appear for cursor pagination of latest messages first
    assert "DESC" in order_sql.upper()
