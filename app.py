import os
from flask import Flask
import asyncio
from neo4j import GraphDatabase
from dotenv import load_dotenv
from Neo4jData import Neo4jData

load_dotenv()
db_uri = os.getenv("DATABASE_URI")
api_username = os.getenv("DATABASE_USERNAME")
api_password = os.getenv("DATABASE_PASSWORD")
db_conn = Neo4jData(db_uri, api_username, api_password)

app = Flask(__name__)


@app.route('/')
async def index():
    return "Hello world!"


@app.route('/employees')
async def get_employees():
    return await db_conn.get_employees()


async def main():
    app.run(debug=True)


if __name__ == '__main__':
    asyncio.run(main())
    greeter = Neo4jData(db_uri, api_username, api_password)
    greeter.print_greeting("hello, world")
    greeter.close()
