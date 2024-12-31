from langchain_core.tools import tool
from dspy_agents.sql_agent.database import (
    table_names,
    info_tables_tool,
    query_sql,
    query_sql_checker,
)
from dspy_agents.main.callbacks import ReActCallback

cache = {}
KEY_LIST_TABLES = "list_tables"
KEY_INFO_TABLES = "info_tables"

cache[KEY_LIST_TABLES] = ""
cache[KEY_INFO_TABLES] = {"count": 1}


def execute_callbacks(react_callbacks: list[ReActCallback], func: callable):
    for cb in react_callbacks:
        func(cb)


# Note that the input string is ignored here but cannot be removed.
def sql_list_tables_wrapper(react_callbacks: list[ReActCallback] = []):
    @tool("list_tables", return_direct=True, parse_docstring=True)
    def sql_list_tables(input: str = "") -> str:
        """Returns all tables in the current database.

        Args:
            input: some random input

        Returns:
            The list of all tables separated by commas.

        """
        global cache
        execute_callbacks(react_callbacks, lambda cb: cb.on_tool("list_tables", {}))
        res = ""
        if len(cache[KEY_LIST_TABLES]) > 0:
            res = cache[KEY_LIST_TABLES]
        else:
            cache[KEY_LIST_TABLES] = table_names()
            res = cache[KEY_LIST_TABLES]
        execute_callbacks(react_callbacks, lambda cb: cb.on_observe(res))
        return res

    return sql_list_tables


def sql_info_tables_wrapper(react_callbacks: list[ReActCallback] = []):
    @tool("info_tables")
    def sql_info_tables(table_list_str: str) -> str:
        """Returns metadata about a list of SQL tables.

        Args:
            table_list_str: list of tables separated by commas

        Returns:
            Schemas and sample rows for the listed tables

        """
        global cache
        execute_callbacks(
            react_callbacks,
            lambda cb: cb.on_tool("info_tables", {"table_list": table_list_str}),
        )
        res = ""
        if (
            table_list_str in cache[KEY_INFO_TABLES]
            and not cache[KEY_INFO_TABLES]["count"] % 10 == 0
        ):
            cache[KEY_INFO_TABLES]["count"] += 1
            res = cache[KEY_INFO_TABLES][table_list_str]
        else:
            cache[KEY_INFO_TABLES][table_list_str] = info_tables_tool(tool_input=table_list_str)
            cache[KEY_INFO_TABLES]["count"] = 1
            res == cache[KEY_INFO_TABLES][table_list_str]
        execute_callbacks(react_callbacks, lambda cb: cb.on_observe(res))
        return res

    return sql_info_tables


def sql_query_wrapper(react_callbacks: list[ReActCallback] = []):
    @tool("sql_db_query", return_direct=True)
    def sql_query(sql: str) -> str:
        """Executes a SQL query

        Args:
            sql: The sql statement to be executed

        Returns:
            The rows with the results of the SQL query

        """
        execute_callbacks(
            react_callbacks, lambda cb: cb.on_tool("sql_db_query", {"sql": sql})
        )
        res = query_sql(tool_input=sql)
        execute_callbacks(react_callbacks, lambda cb: cb.on_observe(res))
        return res

    return sql_query


def sql_query_checker_wrapper(react_callbacks: list[ReActCallback] = []):
    @tool("sql_query_checker", return_direct=True)
    def sql_query_checker(sql: str) -> str:
        """Validates SQL queries to check if the syntax is correct

        Args:
            sql: The sql statement to be checked by the LLM
        """
        execute_callbacks(
            react_callbacks, lambda cb: cb.on_tool("sql_query_checker", {"sql": sql})
        )
        res = query_sql_checker.run(sql)
        execute_callbacks(react_callbacks, lambda cb: cb.on_observe(res))

    return sql_query_checker
