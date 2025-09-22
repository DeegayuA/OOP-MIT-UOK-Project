# Inventory and Sales Management System for Water and Soft Drink Distribution

A project for the Master of Information Technology program at the University of Kelaniya (2024), for the course IMIT 53493 - Object Oriented Programming.

## Group Members:
*   N. P. K. Fernando - FGS/MIT/2024/024
*   A.T.L. Dilan Samarasinghe - FGS/MIT/2024/054
*   K. H. S. Ajitha - FGS/MIT/2024/072
*   A. M. N. D. S. Adhikari - FGS/MIT/2024/075

---

## 1. Introduction

This project is an **Inventory and Sales Management System** designed for **Country Style Foods (Pvt) Ltd.**, a leading beverage company in Sri Lanka operating under the brand name **"SMAK"**.

The system focuses specifically on the bottled water and soft drink product segments. It aims to digitize and streamline inventory tracking, order management, and sales processes, replacing the current manual, paper-based methods.

> **Disclaimer:** This system is developed for academic and educational purposes only and does not represent an actual implementation for Country Style Foods (Pvt) Ltd.

## 2. Overview of the Proposed System

### 2.1 The Problem

The current inventory and sales processes are managed manually using paper files and spreadsheets. This leads to:
*   Data inconsistencies
*   Delayed stock updates
*   Inefficient reporting
*   Hindered real-time decision-making

### 2.2 The Solution

A Python-based desktop application with a Graphical User Interface (GUI) to manage inventory and sales for SMAK's bottled water and soft drink categories. The system is designed to improve accuracy, transparency, and operational efficiency.

## 3. Key Features

The system includes the following core modules:

### ▪️ Inventory Management
- Add, edit, and delete product records.
- Track stock at the batch level (manufacture date, expiry date, batch number, quantity).
- Set reorder levels and manage promotional pricing for near-expiry items.

### ▪️ Sales Management
- Record sales transactions quickly and accurately.
- Automatically update inventory levels upon sale.
- Apply authorized discounts with user verification and audit logs.

### ▪️ Order Management
- Create, receive, and process customer orders through a defined workflow.
- Update order statuses: `Received` -> `Ready to Pack` -> `Ready to Distribute` -> `Completed`.

### ▪️ User Management
- Role-based access control (Admin, Staff).
- Admins can manage user profiles and permissions.
- Logs user activity for accountability and security.

### ▪️ Reporting Module
- Generate daily and weekly reports on sales and inventory.
- Features include sales summaries, stock levels, near-expiry warnings, and reorder alerts.
- Dashboard for quick visual summaries.
- Export reports to standard formats like CSV.

### ▪️ Graphical User Interface (GUI)
- Simple, user-friendly, and intuitive design.
- Clearly labelled menus and guided forms.
- Dashboard displays key statistics like today's sales and inventory alerts.

## 4. Technical Implementation

*   **Language:** Python
*   **Core Principles:** Object-Oriented Programming (OOP)
*   **Database:** SQLite for local data persistence.
*   **Architecture:** Follows a layered design pattern:
    *   **Presentation Layer:** GUI
    *   **Service Layer:** Business Logic (Inventory, Sales, Order, Reporting services)
    *   **Domain Layer:** OOP Classes (User, Product, Category, Batch, Customer, Order)
    *   **Data Access Layer:** SQLite database interaction

This project provides hands-on experience in software development and practical business problem-solving using core OOP concepts.
