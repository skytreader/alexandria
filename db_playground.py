from config import SQLALCHEMY_TEST_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if __name__ == "__main__":
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URI)
    session = sessionmaker(bind=engine)()
