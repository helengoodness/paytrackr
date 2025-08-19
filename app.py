import pyodbc  
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Use a secure random key in production

# Database connection
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=paytrackr_db;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# Create the 'positions' table if it doesn't exist
cursor.execute("""
IF NOT EXISTS (
    SELECT * FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_NAME = 'positions'
)
BEGIN
    CREATE TABLE positions (
        id INT PRIMARY KEY IDENTITY(1,1),
        position_name VARCHAR(100),
        base_salary FLOAT,
        allowance FLOAT,
        deduction FLOAT
    )
END
""")

# Create the 'staff' table if it doesn't exist
cursor.execute("""
IF NOT EXISTS (
    SELECT * FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_NAME = 'staff'
)
BEGIN
    CREATE TABLE staff (
        id INT PRIMARY KEY IDENTITY(1,1),
        full_name VARCHAR(100),
        email VARCHAR(100),
        gender VARCHAR(10),
        department VARCHAR(100),
        position_id INT FOREIGN KEY REFERENCES positions(id),
        date_employed DATE
    )
END
""")
conn.commit()

from datetime import datetime

@app.route('/')
def home():
    # Total staff
    cursor.execute("SELECT COUNT(*) FROM staff")
    total_staff = cursor.fetchone()[0]

    # Payroll cost for current month
    current_month = datetime.now().month
    cursor.execute("""
        SELECT SUM(p.base_salary + p.allowance - p.deduction)
        FROM staff s
        JOIN positions p ON s.position_id = p.id
        WHERE MONTH(s.date_employed) <= ?
    """, current_month)
    total_payroll = cursor.fetchone()[0] or 0

    # Staff per department
    cursor.execute("SELECT department, COUNT(*) FROM staff GROUP BY department")
    department_data = cursor.fetchall()

    # Recent staff
    cursor.execute("""
        SELECT TOP 5 full_name, email, department, date_employed
        FROM staff
        ORDER BY date_employed DESC
    """)
    recent_staff = cursor.fetchall()

    return render_template(
        'index.html',
        total_staff=total_staff,
        total_payroll=total_payroll,
        department_data=department_data,
        recent_staff=recent_staff
    )


# Add staff route
@app.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        gender = request.form.get('gender')
        department = request.form.get('department')
        position_id = request.form.get('position_id')
        date_employed = request.form.get('date_employed')

        try:
            # Check for existing staff email
            cursor.execute("SELECT * FROM staff WHERE email = ?", (email,))
            existing_staff = cursor.fetchone()

            if existing_staff:
                flash('A staff member with this email already exists.', 'warning')
                return redirect(url_for('add_staff'))

            # Insert new staff
            cursor.execute("""
                INSERT INTO staff (full_name, email, gender, department, position_id, date_employed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (full_name, email, gender, department, position_id, date_employed))
            conn.commit()

            flash('Staff added successfully!', 'success')
            return redirect(url_for('add_staff'))

        except Exception as e:
            flash(f'Error adding staff: {str(e)}', 'danger')
            return redirect(url_for('add_staff'))

    # Fetch positions for dropdown
    cursor.execute("SELECT id, position_name FROM positions")
    positions = cursor.fetchall()

    return render_template('add_staff.html', positions=positions)

# Staff list route
@app.route('/staff_list', methods=['GET', 'POST'])
def staff_list():
    if request.method == 'POST':
        # Handle form logic or filters here if any
        pass
    cursor.execute("""
        SELECT s.id, s.full_name, s.email, s.gender, p.position_name, s.date_employed
        FROM staff s
        JOIN positions p ON s.position_id = p.id
    """)
    staff_data = cursor.fetchall()
    return render_template('staff_list.html', staff_list=staff_data)

# Payroll route
@app.route('/payroll')
def payroll():
    query = '''
        SELECT s.full_name, s.email, p.position_name, 
               p.base_salary, p.allowance, p.deduction,
               (p.base_salary + p.allowance - p.deduction) AS net_salary
        FROM staff s
        JOIN positions p ON s.position_id = p.id;
    '''
    cursor.execute(query)
    results = cursor.fetchall()

    columns = [column[0] for column in cursor.description]
    return render_template('payroll.html', payroll_data=results, columns=columns)


if __name__ == '__main__':
    app.run(debug=True)
