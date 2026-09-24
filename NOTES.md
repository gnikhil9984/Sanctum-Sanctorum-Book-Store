# Sanctum Sanctorum — Implementation Notes

## Live URL

https://sanctum-sanctorum-book-store.onrender.com

## What I completed

- ISBN-13 normalization and checksum validation
- duplicate ISBN handling
- book PATCH endpoint
- book search, filters, sorting and pagination
- correct pre-pagination total count
- member email normalization and case-insensitive duplicate detection
- order validation and validation precedence
- tier and bulk discounts
- price snapshots on order items
- atomic application-level stock validation before mutation
- order payment and cancellation lifecycle
- stock restoration on cancellation
- complete loan database fields
- tier-based concurrent loan limits
- restricted-book access rules
- dynamic loan status
- return handling and stock restoration
- capped late fees with partial-day rounding
- member statistics
- top-books report based only on paid orders

## Tests

The `tests/` directory was not modified.

The completed implementation passes the full starter test suite locally with:

```bash
pytest -q
```

or, with uv:

```bash
uv run pytest -q
```

## Architecture decisions

### Thin routers

Routers only define HTTP contracts and dependencies. Business rules live in `app/services`.

### Pydantic for input validation

Request normalization and field-level validation happen before business logic. This keeps invalid input from reaching database operations.

### Injected clock

Business operations that depend on current time receive `get_now` through FastAPI dependency injection. This is required by the specification and makes time-dependent tests deterministic.

### Integer money

All monetary values are integer cents. Discount calculations therefore use integer arithmetic.

### Order price snapshots

`OrderItem.unit_price_cents` records the price at order creation so future catalogue price changes do not rewrite historical order totals.

### Order stock integrity

Every requested book is checked before any stock is decremented. Therefore an invalid multi-item order cannot leave stock partially reserved.

### Computed loan status

Active/overdue/returned is derived from `returned_at` and the current clock because overdue status is time-dependent.

## Trade-offs / production improvements

The take-home uses SQLite and synchronous SQLAlchemy because that is the provided contract. For production I would use PostgreSQL, database migrations, stronger concurrent inventory controls, authentication/authorization, structured logging, observability and automated deployment.

The optional concurrency improvement mentioned by the assignment would be especially relevant when multiple requests can compete for the last copy of a book.

## AI usage

I used ChatGPT as a development assistant for repository analysis,
understanding the specification and tests, implementation suggestions,
debugging, API testing guidance, and documentation.

I did not treat generated code as authoritative. I verified the
implementation against SPEC.md, the existing test suite, and manual
Swagger testing.

One example where AI guidance had to be overridden was around the
repository documentation scope. I reviewed the original assignment
instructions directly and kept the interviewer-provided assignment
documents intact rather than removing them based on an earlier
recommendation.

The final implementation and decisions were reviewed and understood
by me before submission.


## Submission status

- Application deployed successfully to the public URL above.
- Public homepage, `/health`, `/docs`, and `/books` endpoints were verified after deployment.
- Git history has been preserved.
- No `.env`, secrets, `.venv`, or `sanctum.db` files are committed.
