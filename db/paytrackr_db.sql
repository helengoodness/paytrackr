-- staff table
CREATE TABLE staff (
    id INT PRIMARY KEY IDENTITY(1,1),
    full_name VARCHAR(100),
    email VARCHAR(100),
    gender VARCHAR(10),
    department VARCHAR(50),
    position VARCHAR(50),
    date_employed DATE
);

-- salary_structure table
CREATE TABLE salary_structure (
    id INT PRIMARY KEY IDENTITY(1,1),
    staff_id INT FOREIGN KEY REFERENCES staff(id),
    base_salary DECIMAL(10,2),
    housing DECIMAL(10,2),
    transport DECIMAL(10,2),
    bonuses DECIMAL(10,2),
    tax DECIMAL(10,2),
    other_deductions DECIMAL(10,2)
);

-- payroll table
CREATE TABLE payroll (
    id INT PRIMARY KEY IDENTITY(1,1),
    staff_id INT FOREIGN KEY REFERENCES staff(id),
    month VARCHAR(20),
    gross_salary DECIMAL(10,2),
    total_deductions DECIMAL(10,2),
    net_pay DECIMAL(10,2),
    status VARCHAR(20)
);
