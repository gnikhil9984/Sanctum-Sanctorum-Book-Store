# Sanctum Sanctorum — Members' Bookstore

Sanctum Sanctorum is a members-only bookstore and lending library built with
FastAPI. Members can browse books, place orders, borrow books, return loans,
and view their activity and bookstore reports.

The project was completed as a backend engineering take-home assignment,
with a small frontend served by the same FastAPI application.

---

## What the application does

The application handles two main workflows:

- Buying books through orders
- Borrowing books through library loans

It also manages membership tiers, discounts, stock, loan limits, late fees,
member statistics, and best-selling book reports.

---

## Main Features

### Book Catalogue

- Create and update books
- Get a book by ID
- Search by title or author
- Filter restricted books
- Filter by price range
- Sort by title or price
- Paginate book listings
- Validate and normalize ISBN-13 values
- Detect duplicate ISBNs
- Validate stock and prices

### Members

- Create members
- Validate and normalize email addresses
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
- Prevent duplicate books within an order
- Check stock before creating an order
- Reserve stock when an order is created
- Apply membership-based discounts
- Apply the bulk discount for orders with 10 or more items
- Preserve the book price at the time of purchase
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

GET /reports/top-books?limit=5