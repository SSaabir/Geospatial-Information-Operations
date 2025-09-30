import os
import logging
from typing import Optional
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration and connection management class."""
    
    def __init__(self):
        """Initialize database configuration from environment variables."""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'GISDb')
        self.username = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', '')
        
        # Alternative: Use complete DATABASE_URL if provided
        self.database_url = os.getenv('DATABASE_URL')
        
        if not self.database_url:
            self.database_url = self._construct_database_url()
        
        # Connection pool settings
        self.pool_size = int(os.getenv('DB_POOL_SIZE', '5'))
        self.max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '10'))
        self.pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', '30'))
        
        # Engine and session factory
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._langchain_db: Optional[SQLDatabase] = None
    
    def _construct_database_url(self) -> str:
        """Construct database URL from individual components."""
        return f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def get_engine(self) -> Engine:
        """
        Get or create SQLAlchemy engine with connection pooling.
        
        Returns:
            Engine: SQLAlchemy engine instance
        """
        if self._engine is None:
            try:
                self._engine = create_engine(
                    self.database_url,
                    poolclass=QueuePool,
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                    pool_timeout=self.pool_timeout,
                    pool_pre_ping=True,  # Verify connections before use
                    echo=os.getenv('DB_ECHO', 'False').lower() == 'true'  # SQL logging
                )
                logger.info(f"Database engine created successfully for {self.host}:{self.port}/{self.database}")
            except Exception as e:
                logger.error(f"Failed to create database engine: {e}")
                raise
        
        return self._engine
    
    def get_session_factory(self) -> sessionmaker:
        """
        Get or create SQLAlchemy session factory.
        
        Returns:
            sessionmaker: Session factory for creating database sessions
        """
        if self._session_factory is None:
            engine = self.get_engine()
            self._session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
            logger.info("Session factory created successfully")
        
        return self._session_factory
    
    def get_session(self) -> Session:
        """
        Create a new database session.
        
        Returns:
            Session: SQLAlchemy session instance
        
        Usage:
            with db_config.get_session() as session:
                # Your database operations here
                pass
        """
        session_factory = self.get_session_factory()
        return session_factory()
    
    def get_langchain_db(self) -> SQLDatabase:
        """
        Get LangChain SQLDatabase instance for AI agent interactions.
        
        Returns:
            SQLDatabase: LangChain database instance
        """
        if self._langchain_db is None:
            try:
                engine = self.get_engine()
                self._langchain_db = SQLDatabase(engine)
                logger.info("LangChain SQLDatabase created successfully")
            except Exception as e:
                logger.error(f"Failed to create LangChain SQLDatabase: {e}")
                raise
        
        return self._langchain_db
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            engine = self.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                row = result.fetchone()
                if row and row[0] == 1:
                    logger.info("Database connection test successful")
                    return True
                else:
                    logger.error("Database connection test failed: Unexpected result")
                    return False
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_connection_info(self) -> dict:
        """
        Get database connection information (without sensitive data).
        
        Returns:
            dict: Connection information
        """
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'username': self.username,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'pool_timeout': self.pool_timeout
        }
    
    def close_connections(self):
        """Close all database connections and cleanup resources."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database engine disposed")
        
        self._engine = None
        self._session_factory = None
        self._langchain_db = None


class DatabaseManager:
    """Context manager for database sessions with automatic cleanup."""
    
    def __init__(self, db_config: DatabaseConfig):
        """
        Initialize database manager.
        
        Args:
            db_config: DatabaseConfig instance
        """
        self.db_config = db_config
        self.session: Optional[Session] = None
    
    def __enter__(self) -> Session:
        """Enter context manager and create session."""
        self.session = self.db_config.get_session()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and cleanup session."""
        if self.session:
            if exc_type is not None:
                # Rollback on exception
                self.session.rollback()
                logger.error(f"Database session rolled back due to exception: {exc_type.__name__}")
            else:
                # Commit on success
                self.session.commit()
            
            self.session.close()
            self.session = None


# Global database configuration instance
db_config = DatabaseConfig()


# Convenience functions for easy access
def get_database_engine() -> Engine:
    """Get database engine instance."""
    return db_config.get_engine()


def get_database_session() -> Session:
    """Get database session instance."""
    return db_config.get_session()


def get_langchain_database() -> SQLDatabase:
    """Get LangChain SQLDatabase instance."""
    return db_config.get_langchain_db()


def get_database_url() -> str:
    """Get complete database URL."""
    return db_config.database_url


def test_database_connection() -> bool:
    """Test database connection."""
    return db_config.test_connection()


def create_database_manager() -> DatabaseManager:
    """Create database manager context."""
    return DatabaseManager(db_config)


# Example usage functions
def example_usage():
    """Example of how to use the database configuration."""
    
    # Test connection
    if test_database_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
        return
    
    # Using context manager for session handling
    with create_database_manager() as session:
        # Example query
        result = session.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
        table_count = result.fetchone()[0]
        print(f"📊 Number of tables in database: {table_count}")
    
    # Using LangChain database
    langchain_db = get_langchain_database()
    print(f"🔗 LangChain database created: {langchain_db}")
    
    # Connection info
    info = db_config.get_connection_info()
    print(f"🔧 Database info: {info}")


if __name__ == "__main__":
    # Run example when script is executed directly
    example_usage()