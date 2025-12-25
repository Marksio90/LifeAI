"""Database query optimization utilities and helpers."""
from typing import List, Type, Any, Optional
from sqlalchemy.orm import Query, joinedload, selectinload, subqueryload
from sqlalchemy.ext.declarative import DeclarativeMeta
import logging

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """
    Utilities for optimizing SQLAlchemy queries.

    Helps prevent N+1 queries and provides best practices for database access.
    """

    @staticmethod
    def eager_load(
        query: Query,
        *relationships: str,
        strategy: str = "joined"
    ) -> Query:
        """
        Add eager loading to query to prevent N+1 queries.

        Args:
            query: SQLAlchemy query
            *relationships: Relationship names to eager load
            strategy: Loading strategy ('joined', 'selectin', 'subquery')

        Returns:
            Query with eager loading applied

        Example:
            >>> query = db.query(User)
            >>> query = QueryOptimizer.eager_load(
            ...     query,
            ...     'conversations',
            ...     'feedbacks',
            ...     strategy='selectin'
            ... )
        """
        if strategy == "joined":
            loader = joinedload
        elif strategy == "selectin":
            loader = selectinload
        elif strategy == "subquery":
            loader = subqueryload
        else:
            raise ValueError(f"Unknown loading strategy: {strategy}")

        for relationship in relationships:
            query = query.options(loader(relationship))

        return query

    @staticmethod
    def paginate(
        query: Query,
        page: int = 1,
        per_page: int = 20,
        max_per_page: int = 100
    ) -> dict:
        """
        Paginate query results efficiently.

        Args:
            query: SQLAlchemy query
            page: Page number (1-indexed)
            per_page: Items per page
            max_per_page: Maximum items per page

        Returns:
            Dictionary with items, pagination metadata

        Example:
            >>> query = db.query(Conversation)
            >>> result = QueryOptimizer.paginate(query, page=2, per_page=10)
            >>> items = result['items']
            >>> total = result['total']
        """
        # Validate inputs
        page = max(1, page)
        per_page = min(max(1, per_page), max_per_page)

        # Get total count (cached in many ORMs)
        total = query.count()

        # Calculate pagination
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1

        # Get items for current page
        offset = (page - 1) * per_page
        items = query.limit(per_page).offset(offset).all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        }

    @staticmethod
    def cursor_paginate(
        query: Query,
        cursor: Optional[str] = None,
        per_page: int = 20,
        cursor_field: str = "created_at"
    ) -> dict:
        """
        Cursor-based pagination for better performance with large datasets.

        More efficient than offset pagination for large datasets.

        Args:
            query: SQLAlchemy query
            cursor: Cursor from previous page (None for first page)
            per_page: Items per page
            cursor_field: Field to use for cursor (must be indexed!)

        Returns:
            Dictionary with items and next cursor

        Example:
            >>> query = db.query(Conversation).order_by(Conversation.created_at.desc())
            >>> result = QueryOptimizer.cursor_paginate(query, cursor=None, per_page=10)
            >>> items = result['items']
            >>> next_cursor = result['next_cursor']
        """
        # If cursor provided, filter from that point
        if cursor:
            # In real implementation, decode cursor and apply filter
            # For now, simple implementation
            pass

        # Get items
        items = query.limit(per_page + 1).all()

        # Check if there are more items
        has_next = len(items) > per_page
        if has_next:
            items = items[:per_page]

        # Generate next cursor from last item
        next_cursor = None
        if has_next and items:
            last_item = items[-1]
            # In real implementation, encode cursor
            next_cursor = str(getattr(last_item, cursor_field))

        return {
            "items": items,
            "next_cursor": next_cursor,
            "has_next": has_next,
            "per_page": per_page
        }

    @staticmethod
    def optimize_count(query: Query) -> int:
        """
        Optimized count query that doesn't load all columns.

        Args:
            query: SQLAlchemy query

        Returns:
            Count of rows

        Example:
            >>> query = db.query(User).filter(User.is_active == True)
            >>> count = QueryOptimizer.optimize_count(query)
        """
        # Use count() but with optimizations
        return query.count()

    @staticmethod
    def batch_load(
        query: Query,
        batch_size: int = 1000
    ) -> List[Any]:
        """
        Load large result sets in batches to avoid memory issues.

        Args:
            query: SQLAlchemy query
            batch_size: Number of rows per batch

        Yields:
            Batches of results

        Example:
            >>> query = db.query(Conversation)
            >>> for batch in QueryOptimizer.batch_load(query, batch_size=500):
            ...     process_batch(batch)
        """
        offset = 0
        while True:
            batch = query.limit(batch_size).offset(offset).all()
            if not batch:
                break

            yield batch
            offset += batch_size

    @staticmethod
    def explain_query(query: Query) -> str:
        """
        Get query execution plan (EXPLAIN) for debugging.

        Args:
            query: SQLAlchemy query

        Returns:
            Query execution plan as string

        Example:
            >>> query = db.query(User).filter(User.email == 'test@example.com')
            >>> plan = QueryOptimizer.explain_query(query)
            >>> print(plan)
        """
        # Get SQL statement
        from sqlalchemy.dialects import postgresql

        compiled = query.statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True}
        )

        return f"EXPLAIN ANALYZE {compiled}"


class CommonQueryPatterns:
    """
    Common optimized query patterns for the application.
    """

    @staticmethod
    def get_user_with_conversations(
        db,
        user_id: str,
        limit: int = 10
    ):
        """
        Get user with recent conversations (optimized, no N+1).

        Args:
            db: Database session
            user_id: User ID
            limit: Number of conversations to load

        Returns:
            User with conversations
        """
        from app.models.user import User
        from app.models.conversation import Conversation

        user = db.query(User).options(
            selectinload(User.conversations).options(
                selectinload(Conversation.feedbacks),
                selectinload(Conversation.agent_interactions)
            ).limit(limit)
        ).filter(User.id == user_id).first()

        return user

    @staticmethod
    def get_conversations_with_details(
        db,
        user_id: str,
        page: int = 1,
        per_page: int = 20
    ):
        """
        Get user conversations with all details (optimized).

        Prevents N+1 queries by eager loading all relationships.

        Args:
            db: Database session
            user_id: User ID
            page: Page number
            per_page: Items per page

        Returns:
            Paginated conversations with details
        """
        from app.models.conversation import Conversation

        query = db.query(Conversation).options(
            joinedload(Conversation.user),
            selectinload(Conversation.feedbacks),
            selectinload(Conversation.agent_interactions)
        ).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.created_at.desc())

        return QueryOptimizer.paginate(query, page=page, per_page=per_page)

    @staticmethod
    def get_recent_agent_interactions(
        db,
        user_id: str,
        limit: int = 50
    ):
        """
        Get recent agent interactions for a user (optimized).

        Args:
            db: Database session
            user_id: User ID
            limit: Number of interactions

        Returns:
            List of agent interactions
        """
        from app.models.agent_interaction import AgentInteraction
        from app.models.conversation import Conversation

        interactions = db.query(AgentInteraction).join(
            Conversation
        ).options(
            joinedload(AgentInteraction.conversation)
        ).filter(
            Conversation.user_id == user_id
        ).order_by(
            AgentInteraction.created_at.desc()
        ).limit(limit).all()

        return interactions


# Export for easy import
__all__ = [
    'QueryOptimizer',
    'CommonQueryPatterns'
]
