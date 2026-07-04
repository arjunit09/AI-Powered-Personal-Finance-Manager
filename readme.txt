AI-POWERED PERSONAL FINANCE MANAGER FOR EXPENSE TRACKING AND BUDGET ANALYSIS

## Project Description

AI-Powered Personal Finance Manager is a web-based application developed using Flask and SQLite. The system helps users manage their personal finances by tracking income and expenses, setting budgets, analyzing spending patterns, and generating intelligent financial insights.

The application provides an easy-to-use dashboard that enables users to monitor their financial health and make better financial decisions.

## Features

1. User Registration and Login
2. Secure Password Authentication
3. Add Income and Expense Transactions
4. View Transaction History
5. Delete Transactions
6. Budget Management
7. Budget Summary and Monitoring
8. Interactive Analytics Dashboard
9. Smart Financial Insights
10. Financial Health Score
11. AI-Based Expense Prediction
12. Finance Assistant Chatbot
13. Responsive Modern User Interface

## Technology Stack

Frontend:

* HTML5
* CSS3
* Bootstrap 5
* JavaScript

Backend:

* Python
* Flask

Database:

* SQLite3

Libraries Used:

* Werkzeug
* Pandas
* NumPy
* Scikit-Learn
* Plotly

## Database Tables

1. users

   * id
   * name
   * email
   * password

2. transactions

   * id
   * user_id
   * amount
   * type
   * category
   * description
   * date

3. budgets

   * id
   * user_id
   * category
   * budget_limit

## AI Components

1. Smart Insights Engine

   * Identifies highest spending categories.
   * Detects budget violations.
   * Calculates spending behavior.

2. Financial Health Score

   * Evaluates financial condition.
   * Categorizes users as Excellent, Good, Average, or Poor.

3. Expense Prediction Module

   * Uses Linear Regression.
   * Predicts future monthly expenses.

4. Finance Assistant Chatbot

   * Answers finance-related questions.
   * Retrieves information from user transactions and budgets.

## Project Structure

finance_manager/

│
├── app.py
├── predictor.py
├── database.db
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_transaction.html
│   ├── transactions.html
│   ├── budget.html
│   ├── budget_summary.html
│   ├── analytics.html
│   ├── insights.html
│   └── chatbot.html
│
├── static/
│   ├── css/
│   └── images/

## Installation

1. Install Python 3.x

2. Install required packages:

   pip install flask
   pip install pandas
   pip install numpy
   pip install scikit-learn
   pip install plotly

3. Create database tables.

4. Run the application:

   python app.py

5. Open browser:

   http://127.0.0.1:5000

## Project Objectives

* Track personal income and expenses.
* Monitor spending behavior.
* Manage category-wise budgets.
* Provide intelligent financial insights.
* Predict future expenses using machine learning.
* Improve financial awareness and planning.

## Future Enhancements

* PDF Bank Statement Upload
* Email Reports
* Advanced AI Financial Advisor
* Expense Categorization using NLP
* Mobile Application
* Cloud Deployment

## Developed By

B.Tech Information Technology

Final Year Project

AI-Powered Personal Finance Manager for Expense Tracking and Budget Analysis
