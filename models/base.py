import configparser

config = configparser.ConfigParser()
config.read('config.ini')

from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Example: Replace with your actual database URL
DATABASE_URL = config['database']['url']
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ...existing code...

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    mailgun = Column(String(255), nullable=False)
    campaigns = relationship("Campaign", back_populates="user")

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    company_linkedin = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(100), nullable=False)
    action = Column(String(255), nullable=False)
    date_execution = Column(Date, nullable=False)
    user = relationship("User", back_populates="campaigns")

class CampaignLinkedin(Base):
    __tablename__ = "campaigns_linkedin"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    url = Column(String(255), nullable=False)
    date_from = Column(Date, nullable=False)
    status = Column(String(100), nullable=False)

    campaign = relationship("Campaign")
    contact = relationship("Contact")

class CampaignEmail(Base):
    __tablename__ = "campaigns_email"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    email = Column(String(255), nullable=False)
    date_from = Column(Date, nullable=False)
    status = Column(String(100), nullable=False)

    campaign = relationship("Campaign")
    contact = relationship("Contact")

# To create the table(s) in the database
def init_db():
    Base.metadata.create_all(bind=engine)

# ...existing code...