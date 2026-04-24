from database.connection import engine, Base
from database.models import UserIdentity, Embedding, AuditLog

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
