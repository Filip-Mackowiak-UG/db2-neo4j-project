import os
import traceback
import asyncio
from flask import Flask, jsonify, request
from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv
from asgiref.wsgi import WsgiToAsgi

load_dotenv()
db_uri = os.environ.get("NEO4J_URI")
api_username = os.environ.get("NEO4J_USERNAME")
api_password = os.environ.get("NEO4J_PASSWORD")
driver = AsyncGraphDatabase.driver(db_uri, auth=(api_username, api_password), database="neo4j")
app = Flask(__name__)
loop = asyncio.get_event_loop()


@app.errorhandler(Exception)
def error_handler(error):
    status_code = getattr(error, 'code', 500)  # Get the status code if available

    response = {
        'message': str(error.args[0]),
        'error': None if os.getenv("FLASK_ENV") == 'production' else str(error.args[1]),
        'stack': None if os.getenv("FLASK_ENV") == 'production' else traceback.format_exc(),
    }

    return jsonify(response), status_code


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


async def find_employee(tx, employee_id):
    query = f"MATCH (e:Employee) WHERE ID(e) = {employee_id} RETURN e"
    result = await tx.run(query)
    employee = [dict(record['e'].items()) async for record in result]
    return employee


async def check_if_employee_exists(tx, employee_id):
    return any(await find_employee(tx, employee_id))


async def edit_employee(tx, employee_id, data):
    query = """
        MATCH (e:Employee)-[r:WORKS_IN]->(oldDepartment:Department) WHERE ID(e) = $employee_id
        SET e.first_name = 'JSONer', e.last_name = 'Connorer', e.position = 'Backend-end Developer'
        WITH e, r, oldDepartment
        MATCH (newDepartment:Department {name: 'HR'})
        MERGE (e)-[newR:WORKS_IN]->(newDepartment)
        DELETE
          CASE oldDepartment
            WHEN newDepartment THEN NULL
            ELSE r 
          END
        RETURN e
    """
    result = await tx.run(
        query,
        employee_id=int(employee_id),
        first_name=data['first_name'],
        last_name=data['last_name'],
        position=data['position'],
        department=data['department']
    )
    updated_employee = [dict(record['e'].items()) async for record in result]
    return updated_employee[0]


@app.route('/employees/<employee_id>', methods=['PUT'])
async def edit_employee_route(employee_id):
    try:
        data = request.get_json()
        required_fields = ['first_name', 'last_name', 'position', 'department']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields.'}), 400

        async with driver.session() as session:
            if not await session.execute_read(lambda tx: check_if_employee_exists(tx, employee_id)):
                return jsonify({'error': 'Employee not found.'}), 404

            updated_employee = await session.execute_write(lambda tx: edit_employee(tx, employee_id, data))
            return jsonify({'message': 'Employee updated successfully', 'employee': updated_employee})
    except Exception as e:
        raise Exception("Can't update employee", e)


async def delete_employee(tx, employee_id):
    query = """
        MATCH (e:Employee)-[r:WORKS_IN]->(d:Department)
        WHERE ID(e) = $employee_id
        DELETE e, r
        WITH d
        OPTIONAL MATCH (d)<-[manages:MANAGES]-(e)
        DELETE manages
        WITH d, e
        DETACH DELETE d
    """
    await tx.run(query, employee_id=int(employee_id))
    return True


@app.route('/employees/<employee_id>', methods=['DELETE'])
async def delete_employee_route(employee_id):
    async with driver.session() as session:
        try:
            if not await session.execute_read(lambda tx: check_if_employee_exists(tx, employee_id)):
                return jsonify({'error': 'Employee not found.'}), 404

            await session.execute_write(lambda tx: delete_employee(tx, employee_id))

            return jsonify({'message': f'Successfully deleted employee id: {employee_id}'}), 200

        except Exception as e:
            return jsonify({'error': f"Unable to delete employee: {str(e)}"}), 500


async def get_subordinates(tx, employee_id):
    query = """
        MATCH (manager:Employee)-[:MANAGES]->(d:Department)<-[:WORKS_IN]-(subordinate:Employee)
        WHERE ID(manager) = $employee_id
        RETURN subordinate
    """
    result = await tx.run(query, employee_id=int(employee_id))
    subordinates = [dict(record['subordinate'].items()) async for record in result]
    return subordinates


@app.route('/employees/<employee_id>/subordinates', methods=['GET'])
async def get_subordinates_route(employee_id):
    async with driver.session() as session:
        try:
            if not await session.execute_read(lambda tx: check_if_employee_exists(tx, employee_id)):
                return jsonify({'error': 'Employee not found.'}), 404

            subordinates = await session.execute_read(lambda tx: get_subordinates(tx, employee_id))
            return jsonify(subordinates)

        except Exception as e:
            raise Exception("Unable to get subordinates", e)


async def get_employee_department(tx, employee_id):
    query = """
        MATCH (e:Employee)-[:WORKS_IN]->(d:Department)<-[:MANAGES]-(manager:Employee)
        WHERE ID(e) = $employee_id
        WITH d, manager
        OPTIONAL MATCH (d)<-[:WORKS_IN]-(employees:Employee)
        RETURN d.name AS department_name, count(employees) AS num_employees, manager.first_name + ' ' + manager.last_name AS manager_name
    """
    result = await tx.run(query, employee_id=int(employee_id))
    department_info = [dict(record.items()) async for record in result]
    return department_info[0] if department_info else None


@app.route('/employees/<employee_id>/department', methods=['GET'])
async def get_employee_department_route(employee_id):
    try:
        async with driver.session() as session:
            if not await session.execute_read(lambda tx: check_if_employee_exists(tx, employee_id)):
                return jsonify({'error': 'Employee not found.'}), 404

            department_info = await session.execute_read(lambda tx: get_employee_department(tx, employee_id))

            if department_info:
                return jsonify(department_info), 200
            else:
                return jsonify({'error': 'Employee is not assigned to any department.'}), 404

    except Exception as e:
        raise Exception("Unable to retrieve department information", e)


async def get_departments(tx, filter_params=None, order_by_params=None):
    if filter_params is None:
        filter_params = {}
    query = "MATCH (d:Department) WHERE 1=1"

    for key, value in filter_params.items():
        if isinstance(value, str):
            query += f" AND d.{key} ='{value}'"
        elif isinstance(value, (int, float)):
            query += f" AND d.{key}={value}"

    query += " WITH d, [(e)-[:WORKS_IN]->(d) | e] AS employees"
    query += " RETURN d, size(employees) AS num_employees"

    if order_by_params:
        query += f" ORDER BY"
        for order_criterion in order_by_params:
            if order_criterion == "num_employees":
                query += f" {order_criterion},"
            else:
                query += f" d.{order_criterion},"

        # Delete last comma
        query = query.rstrip(',')

    async_result = await tx.run(query)
    departments = [{"department": dict(record['d'].items()), "num_employees": record['num_employees']} async for
                   record in
                   async_result]

    return departments


@app.route('/departments', methods=['GET'])
async def get_departments_route():
    filter_params = {
        'name': request.args.get('name', default=None, type=str)
    }

    order_by_params = request.args.getlist('order_by')

    try:
        async with driver.session() as session:
            departments = await session.execute_read(lambda tx: get_departments(tx, filter_params, order_by_params))
            return jsonify(departments)
    except Exception as e:
        raise Exception("Unable to get departments", e)


async def get_department_employees(tx, department_id):
    query = """
    MATCH (d:Department)<-[:WORKS_IN]-(e:Employee)
    WHERE ID(d) = $department_id
    RETURN e
    """

    async_result = await tx.run(query, department_id=int(department_id))
    employees = [dict(record['e'].items()) async for record in async_result]

    return employees


@app.route('/departments/<department_id>/employees', methods=['GET'])
async def get_department_employees_route(department_id):
    try:
        async with driver.session() as session:
            employees = await session.execute_read(lambda tx: get_department_employees(tx, department_id))
            return jsonify(employees)
    except Exception as e:
        raise Exception("Unable to get department employees", e)


@app.route('/', methods=['GET'])
async def root_route():
    return "Welcome to the great Flask App!"

asgi_app = WsgiToAsgi(app)
