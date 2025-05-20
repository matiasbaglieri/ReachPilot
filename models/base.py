import configparser

config = configparser.ConfigParser()
config.read('config.ini')

from sqlalchemy import create_engine,UniqueConstraint, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = config['database']['url']
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# Define your models here
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    mailgun = Column(String(255), nullable=False)
    campaigns = relationship("Campaign", back_populates="user")
    contacts = relationship("Contact", back_populates="user")

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    company_linkedin = Column(String(455), nullable=True)
    title = Column(String(655), nullable=True)
    city = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    linkedin = Column(String(455), nullable=True)
    tags = Column(String(555), nullable=True)
    status = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="contacts")

    __table_args__ = (
        UniqueConstraint('email', 'user_id', name='uix_email_user_id'),
    )
    
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
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    url = Column(String(255), nullable=False)
    date_from = Column(Date, nullable=False)
    status = Column(String(100), nullable=False)
    action = Column(String(255), nullable=False)

    campaign = relationship("Campaign")
    contact = relationship("Contact")
    user = relationship("User")

class CampaignEmail(Base):
    __tablename__ = "campaigns_email"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date_from = Column(Date, nullable=False)
    status = Column(String(100), nullable=False)
    to = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(String(5000), nullable=False)

    campaign = relationship("Campaign")
    contact = relationship("Contact")
    user = relationship("User")

# To create the table(s) in the database
def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    