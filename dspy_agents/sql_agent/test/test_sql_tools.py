from dspy_agents.sql_agent.sql_tools import (
    sql_list_tables_wrapper,
    sql_info_tables_wrapper,
    sql_query_wrapper,
    sql_query_checker_wrapper,
)


def test_sql_list_tables():
    res = sql_list_tables_wrapper()("")
    check_exists(res)


def test_sql_info_tables():
    res = sql_info_tables_wrapper()("actor")
    check_exists(res)


def test_sql_query():
    res = sql_query_wrapper()("select * from actor")
    check_exists(res)


def test_sql_query_checker():
    res = sql_query_checker_wrapper()("select * from actor")
    check_exists(res)


def check_exists(res: str):
    assert res is not None, "There are no results"
    assert len(res) > 0, "The result is empty"
