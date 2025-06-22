from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE = "sqlite:///data/db.sqlite3"
engine = create_engine(DATABASE, echo=False)

Session = sessionmaker(bind=engine)
session = Session()

# テーブル作成
Base.metadata.create_all(engine)
