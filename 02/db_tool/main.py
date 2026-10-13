from dotenv import load_dotenv, dotenv_values
from faker import Faker

load_dotenv()
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name}, email={self.email})"


engine = create_engine(dotenv_values()["DATABASE_URL"] or "", echo=False)
# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def create_dummy_table_data() -> None:
    with Session() as session:
        users_count = session.query(User).count()
        if users_count > 0:
            print(session.query(User).all())
            return
        faker = Faker()
        for i in range(10):
            session.add(User(name=faker.name(), email=faker.email()))
        session.commit()


def get_user_by_email(email: str) -> User | None:
    """ Return user by email from database """
    with Session() as session:
        user = session.query(User).filter(User.email == email).first()
        return user


def main():
    # create_dummy_table_data()
    # print(get_user_by_email("wendyrice@example.com"))

    model = init_chat_model(
        model="nvidia/nemotron-3.5-lightning-30b-a3b",
        model_provider="nvidia",
        # stream_usage=True,
    )

    db_agent = create_agent(
        model=model,
        tools=[get_user_by_email],
        system_prompt="You are a helpful assistant",
        name="Database Agent",
    )

    inputs = {"messages": [{"role": "user", "content": "my email is wendyrice1@example.com tell me my name"}]}

    result = db_agent.invoke(inputs)
    print(result["messages"][-1].content_blocks)
    pass


if __name__ == '__main__':
    main()
