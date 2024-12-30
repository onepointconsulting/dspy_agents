import re
from typing import Any, Dict, Optional, Sequence, Type, Union
from sqlalchemy import create_engine
from sqlalchemy.inspection import inspect

from pydantic import BaseModel, Field
from langchain.sql_database import SQLDatabase
from langchain_core.language_models import BaseLanguageModel
from langchain_community.tools.sql_database.tool import InfoSQLDatabaseTool
from langchain.tools.sql_database.tool import BaseSQLDatabaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain.tools import BaseTool
from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from sqlalchemy.engine import Result

from dspy_agents.sql_agent import cfg
from dspy_agents.logger import logger

# TODO: consider adding config parameter
LIMIT = 200
LIMIT_EXPRESSION = f" limit {LIMIT};"

engine_sakila = create_engine(cfg.db_connection_sakila, echo=True)
db_sakila = SQLDatabase(engine_sakila)


class _QuerySQLDataBaseToolInput(BaseModel):
    query: str = Field(..., description="A detailed and correct SQL query.")


class QuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name: str = "sql_db_query"
    description: str = """
    Execute a SQL query against the database and get back the result..
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    This method ensures that not more than 1000 results are retrieved.
    """
    args_schema: Type[BaseModel] = _QuerySQLDataBaseToolInput

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[str, Sequence[Dict[str, Any]], Result]:
        """Execute the query, return the results or an error message."""
        # Make sure that the tool is limited to a specific amount of rows, otherwise we might get in trouble.
        query = QuerySQLDataBaseTool.append_limit(query)
        cursor = self.db.run_no_throw(query, fetch="cursor")
        if isinstance(cursor, str):
            return cursor
        res = []
        try:
            for i, x in enumerate(cursor.fetchmany(LIMIT)):
                res.append(x._asdict())
                if i == LIMIT:
                    break
            return str(res)
        except Exception as e:
            logger.exception(f"Cannot process '{query}'")
            return str(e)

    @staticmethod
    def append_limit(query: str) -> str:
        if " limit " not in query.lower():
            query = query.strip()
            query = re.sub(r";$", "", query)
            query += LIMIT_EXPRESSION
        return query


def table_names(schema: str = "sakila") -> str:
    inspect_sakila = inspect(engine_sakila)
    tables = set(
        inspect_sakila.get_table_names(schema=schema)
        + (inspect_sakila.get_view_names(schema=schema))
    )
    sorted_tables = sorted(tables)
    return ", ".join(sorted_tables)


# flake8: noqa
QUERY_CHECKER = """
{query}
Double check the {dialect} query above for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Output the final SQL query only.

SQL Query: """



class QuerySQLCheckerTool():  # type: ignore[override, override]
    """Use an LLM to check if a query is correct.
    Adapted from https://www.patterns.app/blog/2023/01/18/crunchbot-sql-analyst-gpt/
    
    Use this tool to double check if your query is correct before executing it.
    Always use this tool before executing a query with sql_db_query!
    """

    def __init__(self, db: SQLDatabase):
        self.db = db
        self.llm_chain = LLMChain(
                llm=cfg.llm,
                prompt=PromptTemplate(
                    template=QUERY_CHECKER, input_variables=["dialect", "query"]
                ),
            )

        if self.llm_chain.prompt.input_variables != ["dialect", "query"]:
            raise ValueError(
                "LLM chain for QueryCheckerTool must have input variables ['query', 'dialect']"
            )        

    def run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the LLM to check the query."""
        return self.llm_chain.predict(
            query=query,
            dialect=self.db.dialect,
            callbacks=run_manager.get_child() if run_manager else None,
        )


info_tables_tool: BaseTool = InfoSQLDatabaseTool(db=db_sakila)
query_sql: BaseTool = QuerySQLDataBaseTool(db=db_sakila)
query_sql_checker = QuerySQLCheckerTool(db=db_sakila)


if __name__ == "__main__":

    def test_table_names():
        logger.info("Testing DB functions")
        logger.info(cfg.db_connection_sakila)
        res = table_names()
        assert res, "There are no tables"
        logger.info(res)

    test_table_names()
