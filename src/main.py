import uvicorn
from src.core.logging import get_logger
from src.core.database import db

logger = get_logger(__name__)

def main():
    """Main entry point for the application."""
    try:
        # Verify database connection
        db.get_client().admin.command('ping')
        logger.info("Database connection verified")
        
        # Start the FastAPI application
        uvicorn.run(
            "src.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    except Exception as e:
        logger.error("Failed to start application", error=str(e))
        raise

if __name__ == "__main__":
    main() 