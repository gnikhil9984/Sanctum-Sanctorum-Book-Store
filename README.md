# Sanctum Sanctorum — Members' Bookstore

Sanctum Sanctorum is a members-only bookstore and lending library built with
FastAPI. Members can browse books, purchase books, borrow books, return loans,
and view their activity and bookstore reports.

The project was developed as a backend engineering take-home assignment with
a small frontend served by the same FastAPI application.

---

## What the application does

The application supports two main activities:

- Buying books through orders
- Borrowing books through library loans

It also manages membership tiers, discounts, stock, loan limits, late fees,
member statistics, and best-selling-book reports.

---

## Main Features

### Book Catalogue

- Create and update books
- Get a book by ID
- Search by title or author
- Filter restricted books
- Filter by price range
- Sort by title or price
- Pagination
- ISBN-13 validation and normalization
- Duplicate ISBN detection
- Stock and price validation

### Members

- Create members
- Normalize and validate email addresses
- Prevent duplicate member emails
- Support four membership tiers:
  - Apprentice
  - Adept
  - Master
  - Supreme
- View member orders
- View member loans
- View member statistics

### Orders

- Create orders
- Validate order items
- Prevent duplicate books in the same order
- Check book stock before creating an order
- Reserve stock when an order is created
- Apply membership discounts
- Apply the additional bulk discount for 10 or more items
- Keep the original book price in the order
- Pay pending orders
- Cancel pending orders
- Restore stock when an order is cancelled

### Loans

- Borrow books
- Apply membership-based loan limits
- Restrict certain books to Master tier and above
- Prevent duplicate active loans for the same book
- Prevent borrowing when a member has overdue loans
- Calculate loan due dates
- Return books
- Restore stock when a book is returned
- Calculate late fees
- Apply the late-fee cap based on the book price

### Reports

The application provides a best-selling-books report based on paid orders.


## Live Application

The application is deployed and available at:

https://sanctum-sanctorum-book-store.onrender.com

