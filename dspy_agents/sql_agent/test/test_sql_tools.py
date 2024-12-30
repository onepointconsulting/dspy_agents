from dspy_agents.sql_agent.sql_tools import sql_list_tables, sql_info_tables, sql_query, sql_query_checker


def test_sql_list_tables():
    res = sql_list_tables("")
    check_exists(res)


def test_sql_info_tables():
    res = sql_info_tables("actor")
    check_exists(res)


def test_sql_query():
    res = sql_query("select * from actor")
    check_exists(res)


def test_sql_query_checker():
    res = sql_query_checker("select * from actor")
    check_exists(res)


def check_exists(res: str):
    assert res is not None, "There are no results"
    assert len(res) > 0, "The result is empty"