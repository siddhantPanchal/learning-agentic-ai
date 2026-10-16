from dotenv import load_dotenv

load_dotenv()
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from db import *

# Session = init_db(delete_old=True, create=True)


Session = init_db(delete_old=False, create=False)


def get_customer(customer_id: int | None = None, customer_email: str | None = None) -> CustomerSchema | None:
    """Retrieve customer profile information by customer ID or email address.

    At least one parameter must be provided. If both are supplied, customer_id takes precedence.

    Args:
        customer_id (int | None): The unique integer ID of the customer.
        customer_email (str | None): The registered email address of the customer.

    Returns:
        CustomerSchema | None: The customer profile containing 'id', 'name', and 'email'
        if found, or None if no matching customer exists or no arguments are provided.
    """
    if customer_id is None and customer_email is None:
        return None
    with (Session() as session):
        customer: Customer | None
        if customer_id is not None:
            customer = session.query(Customer).filter(Customer.id == customer_id).first()
        elif customer_email is not None:
            customer = session.query(Customer).filter(Customer.email == customer_email).first()
        return CustomerSchema.model_validate(customer) if customer else None


def get_ticket(ticket_id: int | None = None, customer_id: int | None = None) -> TicketSchema | None:
    """Retrieve a single support ticket by its ticket ID or customer ID.

    Use this tool when you need details of a specific ticket (by ticket_id) or the
    first ticket associated with a customer. To retrieve all tickets belonging to a
    customer, use 'get_tickets' instead. At least one parameter must be provided.
    If both are supplied, ticket_id takes precedence.

    Args:
        ticket_id (int | None): The unique integer ID of the ticket to retrieve.
        customer_id (int | None): The customer's integer ID to look up their first ticket.

    Returns:
        TicketSchema | None: The ticket details containing 'id', 'status', 'order_id',
        and 'customer_id' if found, or None if no matching ticket exists or if neither
        parameter is provided.
    """
    if ticket_id is None and customer_id is None:
        return None
    with (Session() as session):
        ticket: Ticket | None
        if ticket_id is not None:
            ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
        elif customer_id is not None:
            ticket = session.query(Ticket).filter(Ticket.customer_id == customer_id).first()
        return TicketSchema.model_validate(ticket) if ticket else None


def get_tickets(customer_id: int) -> list[TicketSchema]:
    """Retrieve all support tickets associated with a specific customer.

    Use this tool to view a customer's complete support ticket history or check current ticket statuses.

    Args:
        customer_id (int): The unique integer ID of the customer.

    Returns:
        list[TicketSchema]: A list of tickets, each containing 'id', 'status',
        'order_id', and 'customer_id'. Returns an empty list if no tickets are found.
    """
    with (Session() as session):
        tickets = session.query(Ticket).filter(Ticket.customer_id == customer_id).all()
        return [TicketSchema.model_validate(ticket) for ticket in tickets]


def get_order(customer_id: int) -> OrderSchema | None:
    """Retrieve the first order found for a specific customer.

    Use this tool to quickly look up order details when the customer only has a single order.
    If the customer may have multiple orders or you need to inspect all of them, use
    'get_orders' instead.

    Args:
        customer_id (int): The unique integer ID of the customer. Must be a valid customer.

    Returns:
        OrderSchema | None: The order details containing 'id', 'status' (REQUESTED,
        IN_PROGRESS, DISPATCHED, DELIVERED, CANCELLED), and 'customer_id', or None if the
        customer has no orders.

    Raises:
        Exception: If no customer with the provided customer_id exists in the database.
    """
    with Session() as session:
        customer = session.query(Customer).filter(Customer.id == customer_id).first()
        if customer is None:
            raise Exception("Customer not found")
        order = session.query(Order).filter(Order.customer_id == customer_id).first()
        return OrderSchema.model_validate(order) if order else None


def get_orders(customer_id: int) -> list[OrderSchema]:
    """Retrieve all orders placed by a specific customer.

    Use this tool when a customer inquires about their order status, delivery progress, or order history.

    Args:
        customer_id (int): The unique integer ID of the customer. Must be a valid customer.

    Returns:
        list[OrderSchema]: A list of all orders belonging to the customer, each containing
        'id', 'status' (REQUESTED, IN_PROGRESS, DISPATCHED, DELIVERED, CANCELLED), license_plate, and
        'customer_id'. Returns an empty list if the customer has placed no orders.

    Raises:
        Exception: If no customer with the provided customer_id exists in the database.
    """
    with Session() as session:
        customer = session.query(Customer).filter(Customer.id == customer_id).first()
        if customer is None:
            raise Exception("Customer not found")
        orders = session.query(Order).filter(Order.customer_id == customer_id).all()
        return [OrderSchema.model_validate(order) for order in orders]


def get_customer_support_agent(support_agent_id: int) -> SupportAgentSchema | None:
    """Retrieve customer support agent profile details by support agent ID.

    Args:
        support_agent_id (int): The unique integer ID of the support agent (e.g., 1).

    Returns:
        SupportAgentSchema | None: The support agent profile containing 'id', 'name',
        and 'email' if found, or None if no support agent with the given ID exists.
    """
    with Session() as session:
        support_agent = session.query(SupportAgent).filter(SupportAgent.id == support_agent_id).first()
        return SupportAgentSchema.model_validate(support_agent) if support_agent else None


def create_ticket(customer_id: int, problem: str, problem_description: str, order_id: int) -> TicketSchema:
    """Create a new customer support ticket linked to a specific customer and order.

    Only call this tool when the customer has explicitly requested creating or escalating a support ticket.

    Args:
        customer_id (int): The unique integer ID of the customer opening the ticket.
            Must be an existing customer ID.
        problem (str): A concise summary or category of the issue (max 100 characters).
            Example: 'Delayed Delivery', 'Damaged Item', 'Order Not Received'.
        problem_description (str): A detailed explanation of the customer's issue or
            escalation reason (max 200 characters).
        order_id (int): The unique integer ID of the order related to this ticket.

    Returns:
        TicketSchema: The newly created ticket with status 'CREATED', containing 'id',
        'status', 'customer_id', 'problem', 'problem_description', and 'order_id'.

    Raises:
        Exception: If no customer with the provided customer_id exists in the database.
    """
    with Session() as session:
        customer = session.query(Customer).filter(Customer.id == customer_id).first()
        if customer is None:
            raise Exception("Customer not found")
        ticket = Ticket(
            customer_id=customer.id, order_id=order_id, problem=problem,
            problem_description=problem_description,
            status=TicketStatus.CREATED
        )
        session.add(ticket)
        session.commit()
        return TicketSchema.model_validate(ticket)


def main():
    """Seed sample data, initialize the customer support agent with tools, and run the interactive chat loop."""
    create_fake_data()
    with Session() as session:
        customers = session.query(SupportAgent).all()
        print([_.name for _ in customers])  # Shannon Holland
        customers = session.query(Customer).all()
        print([_.email for _ in customers])  # Shane Powell, payneemily@example.com

    support_agent = get_customer_support_agent(1)
    agent_name = support_agent.name if support_agent else "Shannon Holland"
    agent_email = support_agent.email if support_agent else "shannon.holland@support.com"

    system_prompt = (
        f"You are {agent_name}, a Customer Support Agent (ID: 1, Email: {agent_email}). Always keep your tone polite.\n\n"
        "Guidelines:\n"
        "1. If the user asks who you are or greets you, introduce yourself directly in text without calling any tools.\n"
        "2. ONLY call tools when the user explicitly asks about specific customer records, orders, or tickets.\n"
        "3. NEVER guess or hallucinate customer IDs or emails.\n"
        "4. As soon as you receive the required tool output, formulate your answer to the user and stop calling tools."
    )

    model = init_chat_model(
        model="nvidia/nemotron-3.5-lightning-30b-a3b",
        model_provider="nvidia",
        # model="llama3.2:3B-F16",
        # model_provider="openai",
        # base_url="http://localhost:12434/v1"
        # stream_usage=True,
    )

    agent = create_agent(
        model=model,
        system_prompt=system_prompt,
        tools=[
            get_customer,
            get_tickets,
            get_ticket,
            get_order,
            get_customer_support_agent,
            create_ticket,
            get_orders
        ]
    )

    query = input("User> ")

    # who you are??
    # my name is Shane Powell and my email is payneemily@example.com, can you get my orders?
    # this order is still in requested please create a new ticket to escalate this further so my will be delivered
    inputs = {"messages": []}

    while query != "exit":
        inputs = {"messages": inputs["messages"] + [{"role": "user", "content": query}]}
        result = agent.invoke(inputs, config={"recursion_limit": 6})
        # Update messages history with all intermediate messages produced
        inputs["messages"] = result["messages"]
        print(f"Agent> {result['messages'][-1].content}")
        query = input("User> ")

    pass


if __name__ == '__main__':
    main()
