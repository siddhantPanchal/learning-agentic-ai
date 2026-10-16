import random
from enum import Enum

from dotenv import dotenv_values
from faker import Faker
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker, mapped_column, Mapped, relationship

db_engine = create_engine(dotenv_values()['DATABASE_URL'] or "", echo=False)
Session = sessionmaker(bind=db_engine)


class Base(DeclarativeBase):
    pass


class TicketStatus(Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    HALTED = "HALTED"
    RESOLVED = "RESOLVED"


class OrderStatus(Enum):
    REQUESTED = "REQUESTED"
    IN_PROGRESS = "IN_PROGRESS"
    DISPATCHED = "DISPATCHED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)


class SupportAgent(Base):
    __tablename__ = "support_agents"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    problem: Mapped[str] = mapped_column(String(100), nullable=False)
    problem_description: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[TicketStatus] = mapped_column(nullable=False)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    order: Mapped["Order"] = relationship()

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship()


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    license_plate: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(nullable=False)

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship()


def init_db(delete_old=False, create=True):
    if delete_old:
        Base.metadata.drop_all(db_engine)
    if create:
        Base.metadata.create_all(db_engine)
    return Session


def create_fake_data(num_customers: int = 5, num_agents: int = 3):
    faker = Faker()
    with Session() as _session:
        customer_count = _session.query(Customer).count()
        if customer_count > 0:
            return
        # 1. Support Agents
        agents = [
            SupportAgent(name=faker.name()[:50], email=faker.unique.email()[:100])
            for _ in range(num_agents)
        ]
        _session.add_all(agents)

        # 2. Customers
        customers = [
            Customer(name=faker.name()[:50], email=faker.unique.email()[:100])
            for _ in range(num_customers)
        ]
        _session.add_all(customers)
        _session.flush()

        # 3. Orders (1-3 per customer)
        orders: list[Order] = []
        for customer in customers:
            for _ in range(random.randint(1, 3)):
                order = Order(
                    status=random.choice(list(OrderStatus)),
                    customer_id=customer.id,
                    license_plate=faker.license_plate(),
                )
                orders.append(order)
        _session.add_all(orders)
        _session.flush()

        # 4. Tickets (associated with an order and its customer)
        tickets = []
        for order in orders:
            # 60% chance of a ticket for each order
            if random.random() < 0.6:
                problem = faker.sentence()
                ticket = Ticket(
                    status=random.choice(list(TicketStatus)),
                    order_id=order.id,
                    customer_id=order.customer_id,
                    problem=problem,
                    problem_description=problem,
                )
                tickets.append(ticket)
        _session.add_all(tickets)

        _session.commit()

        print(f"Generated fake data successfully:")
        print(f" - {len(customers)} Customers")
        print(f" - {len(agents)} Support Agents")
        print(f" - {len(orders)} Orders")
        print(f" - {[print(_.id, _.license_plate) for _ in orders]}")
        print(f" - {len(tickets)} Tickets")


class CustomerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class OrderSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    status: OrderStatus
    customer_id: int
    license_plate: str


class TicketSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    status: TicketStatus
    order_id: int
    customer_id: int
    problem: str
    problem_description: str


class SupportAgentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
