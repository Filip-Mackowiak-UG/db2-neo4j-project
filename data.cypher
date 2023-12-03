CREATE (d1:Department {name: 'HR'})
CREATE (d2:Department {name: 'IT'})
CREATE (d3:Department {name: 'Finance'})
CREATE (d4:Department {name: 'Marketing'})
CREATE (d5:Department {name: 'Operations'})
CREATE (d6:Department {name: 'Sales'})

CREATE (e1:Employee {first_name: 'John', last_name: 'Doe', position: 'Manager', salary: 80000})
CREATE (e2:Employee {first_name: 'Alice', last_name: 'Smith', position: 'HR Specialist', salary: 50000})
CREATE (e3:Employee {first_name: 'Bob', last_name: 'Johnson', position: 'IT Specialist', salary: 60000})
CREATE (e4:Employee {first_name: 'Mary', last_name: 'Williams', position: 'Finance Analyst', salary: 55000})
CREATE (e5:Employee {first_name: 'James', last_name: 'Brown', position: 'Marketing Coordinator', salary: 52000})
CREATE (e6:Employee {first_name: 'Emily', last_name: 'Miller', position: 'Operations Associate', salary: 48000})
CREATE (e7:Employee {first_name: 'Michael', last_name: 'Davis', position: 'Sales Representative', salary: 53000})
CREATE (e8:Employee {first_name: 'Emma', last_name: 'Jones', position: 'Manager', salary: 78000})
CREATE (e9:Employee {first_name: 'John', last_name: 'Clark', position: 'HR Specialist', salary: 52000})
CREATE (e10:Employee {first_name: 'David', last_name: 'Taylor', position: 'IT Specialist', salary: 62000})
CREATE (e11:Employee {first_name: 'Olivia', last_name: 'Moore', position: 'Finance Analyst', salary: 56000})
CREATE (e12:Employee {first_name: 'William', last_name: 'Thomas', position: 'Marketing Coordinator', salary: 53000})
CREATE (e13:Employee {first_name: 'Sophia', last_name: 'Anderson', position: 'Operations Associate', salary: 49000})
CREATE (e14:Employee {first_name: 'Daniel', last_name: 'White', position: 'Sales Representative', salary: 54000})
CREATE (e15:Employee {first_name: 'Liam', last_name: 'Walker', position: 'Manager', salary: 75000})
CREATE (e16:Employee {first_name: 'John', last_name: 'Wilson', position: 'HR Specialist', salary: 52000})
CREATE (e17:Employee {first_name: 'Ethan', last_name: 'Moore', position: 'IT Specialist', salary: 63000})
CREATE (e18:Employee {first_name: 'Isabella', last_name: 'Taylor', position: 'Finance Analyst', salary: 57000})
CREATE (e19:Employee {first_name: 'Mia', last_name: 'Brown', position: 'Marketing Coordinator', salary: 54000})
CREATE (e20:Employee {first_name: 'Benjamin', last_name: 'Jones', position: 'Operations Associate', salary: 50000})
CREATE (e21:Employee {first_name: 'Jack', last_name: 'Davis', position: 'Sales Representative', salary: 55000})
CREATE (e22:Employee {first_name: 'Mason', last_name: 'Smith', position: 'Manager', salary: 72000})
CREATE (e23:Employee {first_name: 'Amelia', last_name: 'Miller', position: 'HR Specialist', salary: 53000})
CREATE (e24:Employee {first_name: 'Elijah', last_name: 'Clark', position: 'IT Specialist', salary: 55000})
CREATE (e25:Employee {first_name: 'Grace', last_name: 'Moore', position: 'Finance Analyst', salary: 55000})

CREATE (e2)-[:WORKS_IN]->(d1)
CREATE (e8)-[:WORKS_IN]->(d1)

CREATE (e3)-[:WORKS_IN]->(d2)
CREATE (e10)-[:WORKS_IN]->(d2)
CREATE (e16)-[:WORKS_IN]->(d2)
CREATE (e22)-[:WORKS_IN]->(d2)

CREATE (e4)-[:WORKS_IN]->(d3)
CREATE (e11)-[:WORKS_IN]->(d3)
CREATE (e18)-[:WORKS_IN]->(d3)
CREATE (e24)-[:WORKS_IN]->(d3)

CREATE (e5)-[:WORKS_IN]->(d4)
CREATE (e12)-[:WORKS_IN]->(d4)
CREATE (e19)-[:WORKS_IN]->(d4)

CREATE (e6)-[:WORKS_IN]->(d5)
CREATE (e13)-[:WORKS_IN]->(d5)
CREATE (e20)-[:WORKS_IN]->(d5)

CREATE (e7)-[:WORKS_IN]->(d6)
CREATE (e14)-[:WORKS_IN]->(d6)
CREATE (e21)-[:WORKS_IN]->(d6)

CREATE (e1)-[:MANAGES]->(d1)
CREATE (e1)-[:WORKS_IN]->(d1)

CREATE (e8)-[:MANAGES]->(d2)
CREATE (e8)-[:WORKS_IN]->(d2)

CREATE (e15)-[:MANAGES]->(d3)
CREATE (e15)-[:WORKS_IN]->(d3)

CREATE (e22)-[:MANAGES]->(d4)
CREATE (e22)-[:WORKS_IN]->(d4)

CREATE (e23)-[:MANAGES]->(d5)
CREATE (e23)-[:WORKS_IN]->(d5)

CREATE (e25)-[:MANAGES]->(d6)
CREATE (e25)-[:WORKS_IN]->(d6)
