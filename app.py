import os
import traceback
import asyncio
import uvicorn
from uvicorn import Config
from flask import Flask, jsonify, request
from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv
from asgiref.wsgi import WsgiToAsgi

load_dotenv()
db_uri = os.getenv("NEO4J_URI")
api_username = os.getenv("NEO4J_USERNAME")
api_password = os.getenv("NEO4J_PASSWORD")
driver = AsyncGraphDatabase.driver(db_uri, auth=(api_username, api_password), database="neo4j")
app = Flask(__name__)
loop = asyncio.get_event_loop()


async def get_employees(tx, filter_params=None, order_by_params=None):
    if filter_params is None:
        filter_params = {}
    query = "MATCH (e:Employee) WHERE 1=1"

    for key, value in filter_params.items():
        if isinstance(value, str):
            query += f" AND e.{key}='{value}'"
        elif isinstance(value, (int, float)):
            query += f" AND e.{key}={value}"

    query += " RETURN e"

    if order_by_params:
        query += f" ORDER BY"
        for order_criterion in order_by_params:
            query += f" e.{order_criterion}"

    async_result = await tx.run(query)
    employees = [dict(record['e'].items()) async for record in async_result]

    return employees


@app.route('/employees', methods=['GET'])
async def get_employees_route():
    filter_params = {
        'first_name': request.args.get('first_name', default=None, type=str),
        'last_name': request.args.get('last_name', default=None, type=str),
        'position': request.args.get('position', default=None, type=str),
        'salary': request.args.get('salary', default=None, type=float),
    }

    order_by_params = request.args.getlist('order_by')

    try:
        async with driver.session() as session:
            employees = await session.execute_read(lambda tx: get_employees(tx, filter_params, order_by_params))
            return jsonify(employees)
    except Exception as e:
        raise Exception("Can't get employees", e)


@app.route('/employees/time', methods=['GET'])
async def get_employees_route_sec():
    await asyncio.sleep(10)
    filter_params = {
        'first_name': request.args.get('first_name', default=None, type=str),
        'last_name': request.args.get('last_name', default=None, type=str),
        'position': request.args.get('position', default=None, type=str),
        'salary': request.args.get('salary', default=None, type=float),
    }

    order_by_params = request.args.getlist('order_by')

    try:
        async with driver.session() as session:
            employees = await session.execute_read(lambda tx: get_employees(tx, filter_params, order_by_params))
            return jsonify(employees)
    except Exception as e:
        raise Exception("Can't get employees", e)


async def find_department(tx, department_name):
    query = "MATCH (d:Department {name: $department_name}) RETURN d"
    result = await tx.run(query, department_name=department_name)
    department = [dict(record['d'].items()) async for record in result]
    return department


async def check_unique_name(tx, first_name, last_name):
    return not await get_employees(tx, {"first_name": first_name, "last_name": last_name})


async def check_if_department_exists(tx, department_name):
    return any(await find_department(tx, department_name))


async def add_employee(tx, first_name, last_name, position, salary, department):
    query = """
    MATCH (d:Department {name: $department_name})
    CREATE (e:Employee {
      first_name: $first_name,
      last_name: $last_name,
      position: $position,
      salary: $salary
    })
    CREATE (e)-[:WORKS_IN]->(d)
    RETURN e;
    """
    result = await tx.run(query, first_name=first_name, last_name=last_name, position=position, salary=salary,
                          department_name=department)
    new_employee = [dict(record['e'].items()) async for record in result]
    return new_employee[0]


@app.route('/employees', methods=['POST'])
async def post_employees_route():
    data = request.get_json()
    required_fields = ['first_name', 'last_name', 'position', 'salary', 'department']

    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields.'}), 400

    first_name = data['first_name']
    last_name = data['last_name']
    position = data['position']
    salary = data['salary']
    department = data['department']

    async with driver.session() as session:
        # Check if the name is unique
        if not await session.execute_read(lambda tx: check_unique_name(tx, first_name, last_name)):
            return jsonify({'error': 'Employee with the same name already exists.'}), 400

        # Check if the department exists
        if not await session.execute_read(lambda tx: check_if_department_exists(tx, department)):
            return jsonify({'error': 'The provided department does not exist.'}), 400

        # Add the new employee
        new_employee = await session.execute_write(
            lambda tx: add_employee(tx, first_name, last_name, position, salary, department))
        print(new_employee)
        return jsonify({'message': 'Employee added successfully', 'employee': new_employee}, 201)


asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    config = Config(app, loop='asyncio', workers=1)
    uvicorn.run(asgi_app, port=5000)
