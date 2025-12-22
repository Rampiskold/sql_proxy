from typing import Annotated

from fastapi import Depends

from infrastructure.config.settings import Settings, get_settings
from infrastructure.database.connection import DatabaseConnectionPool, get_pool
from infrastructure.database.query_validator import QueryValidator
from infrastructure.database.repository import PostgreSQLRepository
from use_cases.execute_query import ExecuteQueryUseCase
from use_cases.get_table_schema import GetTableSchemaUseCase
from use_cases.get_tables import GetTablesUseCase


# Settings dependency
def get_app_settings() -> Settings:
    """FastAPI dependency for settings."""
    return get_settings()


SettingsDep = Annotated[Settings, Depends(get_app_settings)]


# Database pool dependency
def get_database_pool(settings: SettingsDep) -> DatabaseConnectionPool:
    """FastAPI dependency for database pool."""
    return get_pool(settings)


PoolDep = Annotated[DatabaseConnectionPool, Depends(get_database_pool)]


# Repository dependency
def get_repository(pool: PoolDep) -> PostgreSQLRepository:
    """FastAPI dependency for database repository."""
    return PostgreSQLRepository(pool)


RepositoryDep = Annotated[PostgreSQLRepository, Depends(get_repository)]


# Query validator dependency
def get_query_validator() -> QueryValidator:
    """FastAPI dependency for query validator."""
    return QueryValidator()


ValidatorDep = Annotated[QueryValidator, Depends(get_query_validator)]


# Use case dependencies
def get_tables_use_case(repo: RepositoryDep) -> GetTablesUseCase:
    """FastAPI dependency for GetTablesUseCase."""
    return GetTablesUseCase(repo)


def get_schema_use_case(repo: RepositoryDep) -> GetTableSchemaUseCase:
    """FastAPI dependency for GetTableSchemaUseCase."""
    return GetTableSchemaUseCase(repo)


def get_execute_query_use_case(
    repo: RepositoryDep, validator: ValidatorDep
) -> ExecuteQueryUseCase:
    """FastAPI dependency for ExecuteQueryUseCase."""
    return ExecuteQueryUseCase(repo, validator)


GetTablesUseCaseDep = Annotated[GetTablesUseCase, Depends(get_tables_use_case)]
GetSchemaUseCaseDep = Annotated[GetTableSchemaUseCase, Depends(get_schema_use_case)]
ExecuteQueryUseCaseDep = Annotated[ExecuteQueryUseCase, Depends(get_execute_query_use_case)]
