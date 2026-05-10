#!/usr/bin/env python3
"""
Run this ONCE after applying schema.sql to insert a real admin member
with a properly hashed password.

Usage:
    python seed.py
"""

import os
import MySQLdb
from werkzeug.security import generate_password_hash

DB_CONFIG = {
    'host':   '127.0.0.1',
    'user':   'root',
    'passwd': '123',
    'db':     'football_club',
    'charset': 'utf8mb4',
}

ADMIN_EMAIL    = 'admin@fcironwall.com'
ADMIN_PASSWORD = 'Admin1234!'          # change before going live!
ADMIN_NAME     = 'Club Admin'

def main():
    conn = MySQLdb.connect(**DB_CONFIG)
    cur  = conn.cursor()

    hashed = generate_password_hash(ADMIN_PASSWORD)

    # Remove placeholder row inserted by schema.sql, then insert real one
    cur.execute("DELETE FROM members WHERE email = %s", (ADMIN_EMAIL,))
    cur.execute(
        "INSERT INTO members (full_name, email, password_hash, position) VALUES (%s, %s, %s, %s)",
        (ADMIN_NAME, ADMIN_EMAIL, hashed, 'Manager')
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"✓ Admin member created: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print("  → Change the password immediately after first login!")

    # Insert sample news posts (requires the admin member to exist)
    conn2 = MySQLdb.connect(**DB_CONFIG)
    cur2  = conn2.cursor()
    cur2.execute("SELECT id FROM members WHERE email = %s", (ADMIN_EMAIL,))
    row = cur2.fetchone()
    if row:
        admin_id = row[0]
        sample_posts = [
            (admin_id, 'Welcome to FC Ironwall!',
             'We are thrilled to launch our new club website. Stay tuned for match reports, training news, and club announcements right here.',
             'Announcement'),
            (admin_id, 'Pre-Season Training Starts Monday',
             'All players are expected at Ironwall Stadium, Pitch 3, at 07:00 on Monday. Bring your boots and plenty of water — Coach Rivera has a tough session planned!',
             'Training'),
            (admin_id, 'Friendly Win vs Red Lions FC — 3-1',
             'A dominant first-half display put us firmly in control. Goals from Martinez (2) and Kowalski secured the result. Full report to follow.',
             'Match Report'),
        ]
        cur2.executemany(
            "INSERT IGNORE INTO posts (member_id, title, content, category) VALUES (%s, %s, %s, %s)",
            sample_posts
        )
        conn2.commit()
        print("✓ Sample news posts inserted.")
    cur2.close()
    conn2.close()

if __name__ == '__main__':
    main()
