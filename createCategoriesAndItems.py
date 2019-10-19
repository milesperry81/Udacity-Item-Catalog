#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  8 18:25:48 2019

@author: Miles
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///itemCategory.db')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Create default system user to create initial catalog items.

user1 = User(username="System", picture="", email="system@nowhere.com")

# Category for Snowboarding
category1 = Category(name="Snowboarding")

session.add(category1)
session.commit()

item1 = Item(name="Goggles",
             description="tbc",
             category=category1,
             user=user1)

session.add(item1)
session.commit()

item2 = Item(name="Skis",
             description="tbc",
             category=category1,
             user=user1)

session.add(item2)
session.commit()

item3 = Item(name="Jacket",
             description="tbc",
             category=category1,
             user=user1)

session.add(item3)
session.commit()

item4 = Item(name="Boots",
             description="tbc",
             category=category1,
             user=user1)

session.add(item4)
session.commit()

item5 = Item(name="Gloves",
             description="tbc",
             category=category1,
             user=user1)

session.add(item5)
session.commit()


# Category for Paintball
category2 = Category(name="Paintball")

session.add(category2)
session.commit()

item1 = Item(name="Goggles",
             description="tbc",
             category=category2,
             user=user1)

session.add(item1)
session.commit()

item2 = Item(name="Guns",
             description="tbc",
             category=category2,
             user=user1)

session.add(item2)
session.commit()

item3 = Item(name="Camoflage Jacket",
             description="tbc",
             category=category2,
             user=user1)

session.add(item3)
session.commit()

item4 = Item(name="Smoke grenades",
             description="tbc",
             category=category2,
             user=user1)

session.add(item4)
session.commit()

item5 = Item(name="Paintballs",
             description="tbc",
             category=category2,
             user=user1)

session.add(item5)
session.commit()


# Category for Computers
category3 = Category(name="Computing")

session.add(category3)
session.commit()

item1 = Item(name="Monitor",
             description="tbc",
             category=category3,
             user=user1)

session.add(item1)
session.commit()

item2 = Item(name="Laptop",
             description="tbc",
             category=category3,
             user=user1)

session.add(item2)
session.commit()

item3 = Item(name="Keyboard",
             description="tbc",
             category=category3,
             user=user1)

session.add(item3)
session.commit()

item4 = Item(name="Mouse",
             description="tbc",
             category=category3,
             user=user1)

session.add(item4)
session.commit()

item5 = Item(name="Server",
             description="tbc",
             category=category3,
             user=user1)

session.add(item5)
session.commit()

# Category for Surfing
category4 = Category(name="Surfing")

session.add(category4)
session.commit()

# Category for Books
category5 = Category(name="Books")

session.add(category5)
session.commit()

# Category for Aeroplanes
category6 = Category(name="Aeroplanes")

session.add(category6)
session.commit()
