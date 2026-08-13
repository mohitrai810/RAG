from app.core.database import Base, engine
from app.models import Chunk, Document


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully.")