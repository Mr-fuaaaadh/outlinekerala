"""
GraphQL Query Performance Middleware
Logs query execution time, complexity, and slow queries
"""
import time
import logging
from django.db import connection, reset_queries
from django.conf import settings

logger = logging.getLogger('graphql.performance')

class QueryPerformanceMiddleware:
    """Middleware to monitor GraphQL query performance"""
    
    def resolve(self, next, root, info, **args):
        # Start timing
        start_time = time.time()
        
        # Get initial query count
        initial_queries = len(connection.queries) if settings.DEBUG else 0
        
        # Execute the resolver
        result = next(root, info, **args)
        
        # Calculate execution time
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Get query count
        query_count = len(connection.queries) - initial_queries if settings.DEBUG else 0
        
        # Log if slow query (> 1000ms)
        if execution_time > 1000:
            logger.warning(
                f"SLOW QUERY: {info.field_name} took {execution_time:.2f}ms "
                f"with {query_count} database queries"
            )
        elif execution_time > 500:
            logger.info(
                f"Query: {info.field_name} took {execution_time:.2f}ms "
                f"with {query_count} database queries"
            )
        
        # Log N+1 queries (more than 10 queries for a single resolver)
        if query_count > 10:
            logger.warning(
                f"POTENTIAL N+1: {info.field_name} executed {query_count} queries"
            )
        
        return result


class QueryComplexityMiddleware:
    """Middleware to calculate and limit query complexity"""
    
    MAX_COMPLEXITY = 1000
    
    def resolve(self, next, root, info, **args):
        # Calculate complexity (simplified version)
        # In production, use graphql-query-complexity library
        complexity = self._calculate_complexity(info)
        
        if complexity > self.MAX_COMPLEXITY:
            logger.error(f"Query complexity {complexity} exceeds maximum {self.MAX_COMPLEXITY}")
            raise Exception(f"Query too complex: {complexity} (max: {self.MAX_COMPLEXITY})")
        
        return next(root, info, **args)
    
    def _calculate_complexity(self, info):
        """Simple complexity calculation based on field depth"""
        # This is a simplified version
        # For production, integrate graphql-query-complexity
        depth = 0
        current = info
        while current:
            depth += 1
            current = getattr(current, 'parent_type', None)
        
        # Estimate complexity (depth * estimated result count)
        return depth * 10


class DatabaseQueryLogger:
    """Context manager to log database queries"""
    
    def __init__(self, operation_name="GraphQL Query"):
        self.operation_name = operation_name
        self.start_time = None
        self.initial_query_count = 0
        
    def __enter__(self):
        self.start_time = time.time()
        self.initial_query_count = len(connection.queries) if settings.DEBUG else 0
        reset_queries()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = (time.time() - self.start_time) * 1000
        query_count = len(connection.queries) if settings.DEBUG else 0
        
        logger.info(
            f"{self.operation_name} completed in {execution_time:.2f}ms "
            f"with {query_count} database queries"
        )
        
        # Log individual queries if DEBUG
        if settings.DEBUG and query_count > 0:
            for i, query in enumerate(connection.queries, 1):
                logger.debug(f"Query {i}: {query['sql'][:200]}... ({query['time']}s)")
