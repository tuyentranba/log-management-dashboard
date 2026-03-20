"""
Database seed script.

Generates 100,000 realistic log entries with:
- Template-based realistic messages
- Production severity distribution (70/20/8/2)
- 7 different source services
- Timestamps spread across last 30 days
- Target: Complete in under 60 seconds
"""
import asyncio
import random
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import insert
from app.database import AsyncSessionLocal, engine
from app.models import Log, Base


# Realistic log message templates (per CONTEXT.md)
MESSAGE_TEMPLATES = [
    "User login failed for user_{}",
    "User login successful for user_{}",
    "API request timeout on endpoint /api/users",
    "API request completed successfully in {}ms",
    "Database query slow: {}ms on table {}",
    "Database connection pool exhausted",
    "Cache miss for key: user_session_{}",
    "Cache hit for key: product_details_{}",
    "Worker task started: process_{}",
    "Worker task completed: process_{} in {}s",
    "Worker task failed: process_{} - timeout",
    "Payment processing initiated for order_{}",
    "Payment processing completed for order_{}",
    "Payment processing failed for order_{} - insufficient funds",
    "File upload started: {}MB",
    "File upload completed: {} in {}s",
    "Email sent to user_{} successfully",
    "Email failed to user_{} - invalid address",
    "Authentication token expired for user_{}",
    "Rate limit exceeded for IP {}",
    "Webhook received from service_{}",
    "Webhook delivery failed to {}",
    "Scheduled job started: {}",
    "Scheduled job completed: {}",
    "Configuration reloaded successfully",
    "Memory usage high: {}%",
    "CPU usage spike: {}%",
    "Disk space low: {}% remaining",
]

# Tables for database query messages
DB_TABLES = ["users", "orders", "products", "sessions", "payments", "logs"]

# Services representing microservices architecture (per CONTEXT.md: 5-10 sources)
SOURCES = [
    "api-service",
    "auth-service",
    "database",
    "frontend",
    "worker",
    "cache",
    "queue"
]

# Severity distribution (per CONTEXT.md: 70/20/8/2)
SEVERITIES = (
    ["INFO"] * 70 +
    ["WARNING"] * 20 +
    ["ERROR"] * 8 +
    ["CRITICAL"] * 2
)


def generate_realistic_message() -> str:
    """Generate realistic log message from templates."""
    template = random.choice(MESSAGE_TEMPLATES)

    # Fill in template placeholders with realistic values
    if "{}" in template:
        replacements = []
        for _ in range(template.count("{}")):
            # Choose appropriate replacement based on context
            if "user_" in template:
                replacements.append(random.randint(1000, 9999))
            elif "order_" in template:
                replacements.append(random.randint(10000, 99999))
            elif "ms" in template:
                replacements.append(random.randint(10, 5000))
            elif "MB" in template:
                replacements.append(round(random.uniform(0.1, 100.0), 1))
            elif "%" in template:
                replacements.append(random.randint(50, 95))
            elif "table" in template:
                replacements.append(random.choice(DB_TABLES))
            elif "IP" in template:
                replacements.append(f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}")
            else:
                replacements.append(random.randint(1, 999))
        return template.format(*replacements)

    return template


async def seed_database(count: int = 100000):
    """
    Generate and insert realistic log entries using bulk operations.

    Args:
        count: Number of log entries to generate (default: 100,000)

    Performance target: Complete in under 60 seconds
    """
    print(f"Generating {count:,} log entries...")
    start_time = time.time()

    # Generate all log records in memory first (fast)
    base_time = datetime.utcnow() - timedelta(days=30)
    time_increment = (30 * 24 * 60 * 60) / count  # Spread across 30 days

    logs = []
    for i in range(count):
        logs.append({
            "timestamp": base_time + timedelta(seconds=i * time_increment),
            "message": generate_realistic_message(),
            "severity": random.choice(SEVERITIES),
            "source": random.choice(SOURCES)
        })

    generation_time = time.time() - start_time
    print(f"Generated {count:,} logs in {generation_time:.2f}s")

    # Bulk insert using SQLAlchemy (automatically batches for performance)
    print(f"Inserting {count:,} logs into database...")
    insert_start = time.time()

    async with AsyncSessionLocal() as session:
        # Use bulk_insert_mappings for maximum performance
        await session.run_sync(
            lambda sync_session: sync_session.bulk_insert_mappings(Log, logs)
        )
        await session.commit()

    insert_time = time.time() - insert_start
    total_time = time.time() - start_time

    print(f"Inserted {count:,} logs in {insert_time:.2f}s")
    print(f"Total time: {total_time:.2f}s")

    # Performance check
    if total_time > 60:
        print(f"WARNING: Seed script took {total_time:.2f}s (target: <60s)")
    else:
        print(f"Performance target met: {total_time:.2f}s < 60s")

    # Summary statistics
    severity_counts = {}
    for log in logs:
        severity_counts[log["severity"]] = severity_counts.get(log["severity"], 0) + 1

    print("\nSummary:")
    print(f"  Total logs: {count:,}")
    print(f"  Date range: {logs[0]['timestamp'].date()} to {logs[-1]['timestamp'].date()}")
    print(f"  Severity distribution:")
    for severity in ["INFO", "WARNING", "ERROR", "CRITICAL"]:
        count = severity_counts.get(severity, 0)
        percentage = (count / len(logs)) * 100
        print(f"    {severity}: {count:,} ({percentage:.1f}%)")
    print(f"  Sources: {', '.join(SOURCES)}")


async def create_tables():
    """Create database tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    """Main entry point for seed script."""
    print("Logs Dashboard - Database Seed Script")
    print("=" * 50)

    # Create tables first (idempotent - won't fail if exists)
    print("Ensuring database tables exist...")
    await create_tables()
    print("Tables verified")
    print()

    # Seed database
    await seed_database(count=100000)

    # Dispose engine
    await engine.dispose()

    print("\nSeeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
