# ONLOOK PERFORMANCE OPTIMIZATION GUIDE
# Critical fixes to implement immediately

"""
1. DATABASE CONNECTION POOLING
   - Add connection pooling to db.py
   - Implement proper connection management
"""

# Fix for db.py
import mysql.connector.pooling

def get_db_connection():
    try:
        # Use connection pooling
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="onlook_pool",
            pool_size=10,
            host="localhost",
            user="root", 
            password="haruki1315",
            database="onlook",
            autocommit=False
        )
        return pool.get_connection()
    except Exception as e:
        print(f"Error: {e}")
        return None

"""
2. OPTIMIZE SESSION CHECK
   - Exclude static files from session timeout
"""

# Fix for login.py
@app.before_request
def check_session_timeout():
    # Skip session check for static files
    if request.endpoint == 'static':
        return
    
    # Skip for allowed endpoints
    allowed_endpoints = {'home', 'submit_otp', 'static', ...}
    if request.endpoint in allowed_endpoints:
        return
        
    if 'email' not in session:
        return redirect(url_for('logout'))

"""
3. LAZY LOAD IMAGES
   - Don't load image data unless specifically requested
"""

# Fix for public_view.py
def get_missing_persons_list():
    cursor.execute("""
        SELECT person_id, full_name, age, gender, date_last_seen
        FROM missing_person_information mpi
        JOIN case_file cf ON ...
        WHERE cf.approval_status = 'approved'
        ORDER BY cf.date_and_time_reported DESC
        LIMIT 20  -- Add pagination
    """)
    # Don't load image BLOB data in list view

"""
4. ADD CACHING
   - Cache frequently accessed data
"""

from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_missing_persons():
    # Cache the results for 5 minutes
    pass

"""
5. OPTIMIZE QUERIES
   - Combine multiple queries into single JOINs
   - Add proper indexes
"""

# Instead of multiple queries, use single JOIN
cursor.execute("""
    SELECT cf.*, mpi.*, mpls.*, mpm.missing_filetype
    FROM case_file cf
    LEFT JOIN missing_person_media mpm ON cf.media_id = mpm.missing_person_media_id  
    LEFT JOIN missing_person_information mpi ON mpm.missing_person_id = mpi.person_id
    LEFT JOIN missing_person_last_seen mpls ON cf.last_seen_id = mpls.missing_person_last_seen_id
    WHERE cf.approval_status = 'approved'
    ORDER BY cf.date_and_time_reported DESC
    LIMIT 20
""")

"""
6. REDUCE DEBUG MODE OVERHEAD
"""
# In run.py - disable debug in production
if __name__ == "__main__":
    start_email_scheduler()
    app.run(debug=False, port=port)  # Set debug=False

"""
7. ADD DATABASE INDEXES
"""
# Run these SQL commands:
# CREATE INDEX idx_case_approval ON case_file(approval_status);
# CREATE INDEX idx_case_date ON case_file(date_and_time_reported);
# CREATE INDEX idx_accounts_email ON accounts(email);

"""
8. IMPLEMENT PAGINATION
"""
def get_paginated_results(page=1, per_page=10):
    offset = (page - 1) * per_page
    cursor.execute("""
        SELECT ... FROM case_file 
        LIMIT %s OFFSET %s
    """, (per_page, offset))