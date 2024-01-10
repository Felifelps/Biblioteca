from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker

# Set up connection
engine = create_engine('sqlite:///test.db')
metadata = MetaData()

# Reflect existing tables
metadata.reflect(engine)

# Create table instance
user = Table('user', metadata)

# Start session
Session = sessionmaker(bind=engine)
session = Session()

# Creating data
new_user = {
    'name': 'John Doe',
    'email': 'john.doe@example.com',
    'age': 25
}
session.execute(user.insert().values(new_user))
session.commit()
