from flask import Flask, render_template, request,url_for,session,redirect,flash
import sqlite3
from werkzeug.security import generate_password_hash,check_password_hash
import pandas as pd
import plotly.express as px
import plotly
import json
from predictor import predict_next_month_expense
app = Flask(__name__)

app.secret_key = "finance_manager_secret_key"
@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]

        password = generate_password_hash(
            request.form["password"]
        )

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO users(name,email,password)
                VALUES(?,?,?)
                """,
                (name, email, password)
            )

            conn.commit()

            flash(
                "Registration successful. Please login.",
                "success"
            )

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            flash(
                "Email already exists.",
                "danger"
            )

        finally:

            conn.close()

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, name, email, password
            FROM users
            WHERE email=?
            """,
            (email,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(
            user[3],
            password
        ):

            session["user_id"] = user[0]
            session["user_name"] = user[1]

            flash(
                f"Welcome {user[1]}!",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid Email or Password",
            "danger"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "login.html"
    )

@app.route("/dashboard")
def dashboard():
    flash("Welcome to Dashboard!", "success")
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Total Income
    cursor.execute("""
    SELECT COALESCE(SUM(amount),0)
    FROM transactions
    WHERE user_id=?
    AND type='income'
    """, (session["user_id"],))

    total_income = cursor.fetchone()[0]

    # Total Expense
    cursor.execute("""
    SELECT COALESCE(SUM(amount),0)
    FROM transactions
    WHERE user_id=?
    AND type='expense'
    """, (session["user_id"],))

    total_expense = cursor.fetchone()[0]

    savings = total_income - total_expense
    # Financial Health Score

    score = 100

    budget_exceeded_count = 0

    cursor.execute("""
    SELECT category, budget_limit
    FROM budgets
    WHERE user_id=?
    """, (session["user_id"],))

    budgets = cursor.fetchall()

    for category, limit in budgets:

        cursor.execute("""
        SELECT COALESCE(SUM(amount),0)
        FROM transactions
        WHERE user_id=?
        AND category=?
        AND type='expense'
        """,
        (
            session["user_id"],
            category
        ))

        spent = cursor.fetchone()[0]

        if spent > limit:
            budget_exceeded_count += 1

    if total_income > 0:

        savings_rate = (
            (savings / total_income) * 100
        )

        if savings_rate < 10:
            score -= 30

        elif savings_rate < 20:
            score -= 15

    score -= (budget_exceeded_count * 10)

    score = max(0, min(100, round(score)))
    if score >= 80:
        health_status = "Excellent"

    elif score >= 60:
        health_status = "Good"

    elif score >= 40:
        health_status = "Average"

    else:
        health_status = "Poor"

    # Recent Transactions
    cursor.execute("""
    SELECT category,
           amount,
           date
    FROM transactions
    WHERE user_id=?
    ORDER BY id DESC
    LIMIT 5
    """, (session["user_id"],))

    recent_transactions = cursor.fetchall()

    # Top Expense Category
    cursor.execute("""
    SELECT category,
           COALESCE(SUM(amount),0) as total
    FROM transactions
    WHERE user_id=?
    AND type='expense'
    GROUP BY category
    ORDER BY total DESC
    LIMIT 1
    """, (session["user_id"],))

    top_category = cursor.fetchone()

    
    # Expense Prediction

    cursor.execute("""
    SELECT date, amount
    FROM transactions
    WHERE user_id=?
    AND type='expense'
    ORDER BY date
    """, (session["user_id"],))

    expense_data = cursor.fetchall()

    predicted_expense = predict_next_month_expense(
        expense_data
    )
    conn.close()
    return render_template(
        "dashboard.html",
        name=session["user_name"],
        income=total_income,
        expense=total_expense,
        savings=savings,
        recent_transactions=recent_transactions,
        top_category=top_category,
        score=score,
        health_status=health_status,
        predicted_expense=predicted_expense
    )
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))
@app.route("/add_transaction", methods=["GET", "POST"])
def add_transaction():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        amount = request.form["amount"]
        trans_type = request.form["type"]
        category = request.form["category"]
        description = request.form["description"]
        date = request.form["date"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO transactions
        (user_id, amount, type, category, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            amount,
            trans_type,
            category,
            description,
            date
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("view_transactions"))

    return render_template("add_transaction.html")
@app.route("/transactions")
def view_transactions():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, amount, type, category,
           description, date
    FROM transactions
    WHERE user_id = ?
    ORDER BY date DESC
    """, (session["user_id"],))

    transactions = cursor.fetchall()

    conn.close()

    return render_template(
        "transactions.html",
        transactions=transactions
    )
@app.route("/delete_transaction/<int:id>")
def delete_transaction(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM transactions
    WHERE id=?
    AND user_id=?
    """,
    (
        id,
        session["user_id"]
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("view_transactions"))
@app.route("/budget", methods=["GET", "POST"])
def budget():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        category = request.form["category"]
        budget_limit = request.form["budget_limit"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        DELETE FROM budgets
        WHERE user_id=?
        AND category=?
        """,
        (
            session["user_id"],
            category
        ))

        cursor.execute("""
        INSERT INTO budgets
        (
            user_id,
            category,
            budget_limit
        )
        VALUES (?,?,?)
        """,
        (
            session["user_id"],
            category,
            budget_limit
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("budget_summary"))

    return render_template("budget.html")
@app.route("/budget_summary")
def budget_summary():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT category, budget_limit
    FROM budgets
    WHERE user_id=?
    """, (session["user_id"],))

    budgets = cursor.fetchall()

    result = []

    for category, limit in budgets:

        cursor.execute("""
        SELECT COALESCE(SUM(amount),0)
        FROM transactions
        WHERE user_id=?
        AND category=?
        AND type='expense'
        """,
        (
            session["user_id"],
            category
        ))

        spent = cursor.fetchone()[0]

        remaining = limit - spent

        used_percentage = 0

        if limit > 0:
            used_percentage = round(
                (spent / limit) * 100,
                2
            )

        result.append(
            (
                category,
                limit,
                spent,
                remaining,
                used_percentage
            )
        )

    conn.close()

    return render_template(
        "budget_summary.html",
        budgets=result
    )
@app.route("/analytics")
def analytics():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")

    query = """
    SELECT category,
           SUM(amount) as total
    FROM transactions
    WHERE user_id = ?
    AND type = 'expense'
    GROUP BY category
    """
    trend_query = """
    SELECT
        substr(date,1,7) as month,
        SUM(amount) as total
    FROM transactions
    WHERE user_id=?
    AND type='expense'
    GROUP BY substr(date,1,7)
    ORDER BY month
    """

    trend_df = pd.read_sql_query(
        trend_query,
        conn,
        params=(session["user_id"],)
    )
    trend_graph_json = None

    if not trend_df.empty:

        trend_fig = px.line(
            trend_df,
            x="month",
            y="total",
            title="Monthly Expense Trend",
            markers=True
        )

        trend_graph_json = json.dumps(
            trend_fig,
            cls=plotly.utils.PlotlyJSONEncoder
        )
    df = pd.read_sql_query(
        query,
        conn,
        params=(session["user_id"],)
    )
    income_expense_query = """
    SELECT type,
        SUM(amount) as total
    FROM transactions
    WHERE user_id=?
    GROUP BY type
    """

    income_expense_df = pd.read_sql_query(
        income_expense_query,
        conn,
        params=(session["user_id"],)
    )
    conn.close()

    if df.empty:
        graph_json = None
    else:

        fig = px.pie(
            df,
            names="category",
            values="total",
            title="Expense Breakdown by Category"
        )

        graph_json = json.dumps(
            fig,
            cls=plotly.utils.PlotlyJSONEncoder
        )
    bar_graph_json = None

    if not income_expense_df.empty:

        bar_fig = px.bar(
            income_expense_df,
            x="type",
            y="total",
            title="Income vs Expense"
        )

        bar_graph_json = json.dumps(
            bar_fig,
            cls=plotly.utils.PlotlyJSONEncoder
        )
    return render_template(
        "analytics.html",
        graph_json=graph_json,
        trend_graph_json=trend_graph_json,
        bar_graph_json=bar_graph_json
    )
@app.route("/insights")
def insights():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    insights_list = []

    # Highest expense category
    cursor.execute("""
    SELECT category,
           SUM(amount) as total
    FROM transactions
    WHERE user_id=?
    AND type='expense'
    GROUP BY category
    ORDER BY total DESC
    LIMIT 1
    """, (session["user_id"],))

    top_category = cursor.fetchone()

    if top_category:
        insights_list.append(
            f"{top_category[0]} is your highest expense category."
        )

    # Income
    cursor.execute("""
    SELECT COALESCE(SUM(amount),0)
    FROM transactions
    WHERE user_id=?
    AND type='income'
    """, (session["user_id"],))

    income = cursor.fetchone()[0]

    # Expense
    cursor.execute("""
    SELECT COALESCE(SUM(amount),0)
    FROM transactions
    WHERE user_id=?
    AND type='expense'
    """, (session["user_id"],))

    expense = cursor.fetchone()[0]

    if income > 0:

        percent = round(
            (expense / income) * 100,
            2
        )

        insights_list.append(
            f"You spent {percent}% of your income."
        )

    # Budget Analysis
    cursor.execute("""
    SELECT category, budget_limit
    FROM budgets
    WHERE user_id=?
    """, (session["user_id"],))

    budgets = cursor.fetchall()

    for category, limit in budgets:

        cursor.execute("""
        SELECT COALESCE(SUM(amount),0)
        FROM transactions
        WHERE user_id=?
        AND category=?
        AND type='expense'
        """,
        (
            session["user_id"],
            category
        ))

        spent = cursor.fetchone()[0]

        if spent > limit:

            exceeded = round(
                spent - limit,
                2
            )

            insights_list.append(
                f"{category} budget exceeded by ₹{exceeded}"
            )

    if not insights_list:
        insights_list.append(
            "No financial insights available yet. Add transactions and budgets to generate insights."
        )

    conn.close()

    return render_template(
        "insights.html",
        insights=insights_list
    )
@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_query = ""
    response = ""

    if request.method == "POST":

        user_query = request.form["query"].lower()

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Total Expense
        if "expense" in user_query and "prediction" not in user_query:

            cursor.execute("""
            SELECT COALESCE(SUM(amount),0)
            FROM transactions
            WHERE user_id=?
            AND type='expense'
            """, (session["user_id"],))

            total = cursor.fetchone()[0]

            response = f"Your total expenses are ₹{total}"

        # Total Income
        elif "income" in user_query:

            cursor.execute("""
            SELECT COALESCE(SUM(amount),0)
            FROM transactions
            WHERE user_id=?
            AND type='income'
            """, (session["user_id"],))

            total = cursor.fetchone()[0]

            response = f"Your total income is ₹{total}"

        # Savings
        elif "saving" in user_query:

            cursor.execute("""
            SELECT COALESCE(
                SUM(CASE WHEN type='income' THEN amount END),0
            ),
            COALESCE(
                SUM(CASE WHEN type='expense' THEN amount END),0
            )
            FROM transactions
            WHERE user_id=?
            """, (session["user_id"],))

            income, expense = cursor.fetchone()

            response = (
                f"Your savings are ₹{income-expense}"
            )

        # Highest Category
        elif "highest" in user_query or "category" in user_query:

            cursor.execute("""
            SELECT category,
                   SUM(amount) as total
            FROM transactions
            WHERE user_id=?
            AND type='expense'
            GROUP BY category
            ORDER BY total DESC
            LIMIT 1
            """, (session["user_id"],))

            result = cursor.fetchone()

            if result:

                response = (
                    f"Your highest expense category "
                    f"is {result[0]} "
                    f"with ₹{result[1]}"
                )

            else:

                response = "No expense data available."

        else:

            response = (
                "Sorry, I don't understand that question yet."
            )

        conn.close()

    return render_template(
        "chatbot.html",
        user_query=user_query,
        response=response
    )
if __name__ == "__main__":
    app.run(debug=True)