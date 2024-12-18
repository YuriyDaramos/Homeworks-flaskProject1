from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, Text, types
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    ipn = Column(Integer)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20))
    email = Column(String(100), unique=True, nullable=False)
    avatar = Column(String(255))
    register_date = Column(Integer)
    compare_items = Column(types.JSON, default=[], nullable=True)

    items = relationship("Item", backref="owner_user")

    def __init__(self, login, password, email, ipn=None, first_name=None,
                 last_name=None, phone_number=None, avatar=None, register_date=None):
        self.login = login
        self.password = password
        self.email = email
        self.ipn = ipn
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.avatar = avatar
        self.register_date = register_date

    def __repr__(self):
        return f"<User {self.login}>"


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    photo = Column(String(255))
    name = Column(String(255), nullable=False)
    desc = Column(Text)
    price_h = Column(Numeric(10, 2), nullable=True)
    price_d = Column(Numeric(10, 2), nullable=True)
    price_w = Column(Numeric(10, 2), nullable=True)
    price_m = Column(Numeric(10, 2), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", backref="owner_items")

    def __init__(self, name, owner_id, photo=None, desc=None, price_h=None,
                 price_d=None, price_w=None, price_m=None):
        self.name = name
        self.owner_id = owner_id
        self.photo = photo
        self.desc = desc
        self.price_h = price_h
        self.price_d = price_d
        self.price_w = price_w
        self.price_m = price_m

    def __repr__(self):
        return f"<Item {self.name}>"


class Contract(Base):
    __tablename__ = "contracts"

    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    text = Column(Integer)
    date_start = Column(String(100))
    date_end = Column(String(100))
    owner_id = Column(Integer, ForeignKey("users.id"))
    renter_id = Column(Integer, ForeignKey("users.id"))
    is_available = Column(Boolean)

    item = relationship("Item", backref="contracts")
    owner = relationship("User", foreign_keys=[owner_id])
    renter = relationship("User", foreign_keys=[renter_id])

    def __init__(self, item_id, owner_id, renter_id, text=None,
                 date_start=None, date_end=None, is_available=None):
        self.item_id = item_id
        self.owner_id = owner_id
        self.renter_id = renter_id
        self.text = text
        self.date_start = date_start
        self.date_end = date_end
        self.is_available = is_available

    def __repr__(self):
        return f"<Contract {self.item_id}>"


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    grade = Column(Integer, nullable=False)
    contract = Column(Integer, ForeignKey("contracts.item_id"), nullable=False)

    user_relationship = relationship("User", foreign_keys=[user], backref="feedback_received")
    author_relationship = relationship("User", foreign_keys=[author], backref="feedback_given")
    contract_relationship = relationship("Contract", backref="feedback")

    def __init__(self, user, author, text, grade, contract):
        self.user = user
        self.author = author
        self.text = text
        self.grade = grade
        self.contract = contract

    def __repr__(self):
        return f"<Feedback id={self.id} user={self.user} author={self.author}>"


class Favourite(Base):
    __tablename__ = "favourites"

    user = Column(Integer, ForeignKey("users.id"), primary_key=True)
    item = Column(Integer, ForeignKey("items.id"), primary_key=True)

    user_relationship = relationship("User", backref="favourites")
    item_relationship = relationship("Item", backref="favourited_by")

    def __init__(self, user, item):
        self.user = user
        self.item = item

    def __repr__(self):
        return f"<Favourite user={self.user} item={self.item}>"


class SearchHistory(Base):
    __tablename__ = "search_history"

    user = Column(Integer, ForeignKey("users.id"), primary_key=True)
    search_text = Column(Text, nullable=False)
    timestamp = Column(String, nullable=False)

    user_relationship = relationship("User", backref="search_history")

    def __init__(self, user, search_text, timestamp):
        self.user = user
        self.search_text = search_text
        self.timestamp = timestamp

    def __repr__(self):
        return f"<SearchHistory user={self.user} search_text='{self.search_text}' timestamp={self.timestamp}>"
