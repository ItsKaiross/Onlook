#!/usr/bin/env python3
import mysql.connector
from faker import Faker
import bcrypt
from datetime import datetime, timedelta
import random
import os

fake = Faker()

# Database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="haruki1315",
            database="onlook",
            autocommit=False,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def create_fake_users(count=20):
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    for i in range(count):
        # Generate user data
        first_name = fake.first_name()
        middle_name = fake.first_name()
        last_name = fake.last_name()
        suffix = random.choice(['Jr.', 'Sr.', 'III', '']) if random.random() < 0.2 else ''
        gender = random.choice(['Male', 'Female'])
        date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=70)
        contact_number = fake.phone_number()[:15]
        email = fake.email()
        
        # Address - Laguna specific
        house_number = str(fake.building_number())
        street = fake.street_name()
        barangay = random.choice(['Poblacion', 'San Antonio', 'San Jose', 'Santa Cruz', 'Bagumbayan', 'Calumpang', 'Mayapa', 'Batong Malake'])
        city = random.choice(['Los Baños', 'Bay', 'Calamba', 'Santa Rosa', 'Biñan', 'San Pedro', 'Cabuyao', 'Sta. Cruz', 'Pila', 'Victoria', 'Nagcarlan', 'Liliw', 'Magdalena', 'Majayjay', 'Pagsanjan', 'Lumban', 'Kalayaan', 'Cavinti', 'Famy', 'Siniloan', 'Santa Maria', 'Mabitac', 'Pakil', 'Pangil', 'Paete', 'Luisiana', 'Rizal', 'Calauan', 'Alaminos'])
        province = 'Laguna'
        region = 'CALABARZON'
        address = f"{house_number}, {street}, {barangay}, {city}, {province}, {region}"
        
        created_at = datetime.now()
        
        try:
            # Insert into public_user
            cursor.execute("""
                INSERT INTO public_user (
                    first_name, middle_name, last_name, suffix, gender, date_of_birth,
                    contact_number, email, address, house_no, street, barangay,
                    city, province, region, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, middle_name, last_name, suffix, gender, date_of_birth,
                  contact_number, email, address, house_number, street, barangay,
                  city, province, region, created_at))
            
            user_id = cursor.lastrowid
            
            # Create account
            password = "password123"
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute("""
                INSERT INTO accounts (email, password, role, user_id, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (email, hashed_password, 'user', user_id, 'active', created_at))
            
            print(f"Created user {i+1}: {first_name} {last_name} ({email})")
            
        except Exception as e:
            print(f"Error creating user {i+1}: {e}")
            conn.rollback()
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Successfully created {count} users")

def create_fake_police_officers(count=20):
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    ranks = ['Police Officer I', 'Police Officer II', 'Police Officer III', 'Senior Police Officer I', 
             'Senior Police Officer II', 'Senior Police Officer III', 'Police Master Sergeant',
             'Police Staff Sergeant', 'Police Corporal', 'Police Lieutenant']
    
    stations = ['Station 1', 'Station 2', 'Station 3', 'Station 4', 'Station 5', 'Headquarters']
    positions = ['Patrol Officer', 'Detective', 'Traffic Officer', 'Investigator', 'Desk Officer']
    
    # Distribute across 12 months
    months = list(range(1, 13))
    
    for i in range(count):
        # Generate police data
        badge_number = f"PO{str(i+1).zfill(4)}"
        rank = random.choice(ranks)
        first_name = fake.first_name()
        middle_name = fake.first_name()
        last_name = fake.last_name()
        suffix = random.choice(['Jr.', 'Sr.', 'III', '']) if random.random() < 0.2 else ''
        gender = random.choice(['Male', 'Female'])
        date_of_birth = fake.date_of_birth(minimum_age=25, maximum_age=55)
        contact_number = fake.phone_number()[:15]
        email = fake.email()
        
        station = random.choice(stations)
        position = random.choice(positions)
        police_status = 'active'
        
        # Distribute date_joined across different months
        month = months[i % 12]  # Distribute evenly across 12 months
        year = random.choice([2020, 2021, 2022, 2023, 2024])
        day = random.randint(1, 28)  # Safe day for all months
        date_joined = datetime(year, month, day).date()
        
        # Address - Laguna specific
        house_number = str(fake.building_number())
        street = fake.street_name()
        barangay = random.choice(['Poblacion', 'San Antonio', 'San Jose', 'Santa Cruz', 'Bagumbayan', 'Calumpang', 'Mayapa', 'Batong Malake'])
        city = random.choice(['Los Baños', 'Bay', 'Calamba', 'Santa Rosa', 'Biñan', 'San Pedro', 'Cabuyao', 'Sta. Cruz', 'Pila', 'Victoria', 'Nagcarlan', 'Liliw', 'Magdalena', 'Majayjay', 'Pagsanjan', 'Lumban', 'Kalayaan', 'Cavinti', 'Famy', 'Siniloan', 'Santa Maria', 'Mabitac', 'Pakil', 'Pangil', 'Paete', 'Luisiana', 'Rizal', 'Calauan', 'Alaminos'])
        province = 'Laguna'
        region = 'CALABARZON'
        address = f"{house_number}, {street}, {barangay}, {city}, {province}, {region}"
        
        try:
            # Insert into police
            cursor.execute("""
                INSERT INTO police (
                    badge_number, `rank`, first_name, middle_name, last_name, suffix,
                    gender, date_of_birth, contact_number, email, station_assignment,
                    position_title, status, date_joined, address, house_no, street,
                    barangay, city, province, region
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (badge_number, rank, first_name, middle_name, last_name, suffix,
                  gender, date_of_birth, contact_number, email, station, position,
                  police_status, date_joined, address, house_number, street,
                  barangay, city, province, region))
            
            officer_id = cursor.lastrowid
            
            # Create account (password is badge number)
            hashed_password = bcrypt.hashpw(badge_number.encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute("""
                INSERT INTO accounts (email, password, role, status, officer_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (email, hashed_password, 'police', 'active', officer_id, datetime.now()))
            
            print(f"Created police officer {i+1}: {rank} {first_name} {last_name} (Badge: {badge_number}, Joined: {date_joined.strftime('%B %Y')})")
            
        except Exception as e:
            print(f"Error creating police officer {i+1}: {e}")
            conn.rollback()
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Successfully created {count} police officers")

def create_missing_person_reports(count=20):
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Get user IDs
    cursor.execute("SELECT user_id FROM public_user LIMIT %s", (count,))
    users = cursor.fetchall()
    
    if len(users) < count:
        print(f"Not enough users found. Only {len(users)} users available.")
        count = len(users)
    
    # Distribute across 12 months
    months = list(range(1, 13))
    
    for i in range(count):
        user_id = users[i][0]
        
        # Generate missing person data
        first_name = fake.first_name()
        middle_name = fake.first_name()
        last_name = fake.last_name()
        suffix = random.choice(['Jr.', 'Sr.', 'III', '']) if random.random() < 0.2 else ''
        nickname = fake.first_name() if random.random() < 0.5 else ''
        gender = random.choice(['Male', 'Female'])
        date_of_birth = fake.date_of_birth(minimum_age=5, maximum_age=80)
        civil_status = random.choice(['Single', 'Married', 'Divorced', 'Widowed'])
        citizenship = 'Filipino'
        contact_number = fake.phone_number()[:15]
        
        # Physical characteristics - height in feet format
        feet = random.randint(4, 6)
        inches = random.randint(0, 11)
        height = f"{feet}'{inches}\""
        weight = random.randint(40, 100)   # as float
        hair_color = random.choice(['Black', 'Brown', 'Blonde', 'Gray', 'White'])
        eye_color = random.choice(['Brown', 'Black', 'Blue', 'Green', 'Hazel'])
        distinguishing_mark = fake.text(max_nb_chars=100) if random.random() < 0.7 else ''
        
        occupation = fake.job()
        
        # Address - Laguna specific
        house_number = str(fake.building_number())
        street = fake.street_name()
        barangay = random.choice(['Poblacion', 'San Antonio', 'San Jose', 'Santa Cruz', 'Bagumbayan', 'Calumpang', 'Mayapa', 'Batong Malake'])
        city = random.choice(['Los Baños', 'Bay', 'Calamba', 'Santa Rosa', 'Biñan', 'San Pedro', 'Cabuyao', 'Sta. Cruz', 'Pila', 'Victoria', 'Nagcarlan', 'Liliw', 'Magdalena', 'Majayjay', 'Pagsanjan', 'Lumban', 'Kalayaan', 'Cavinti', 'Famy', 'Siniloan', 'Santa Maria', 'Mabitac', 'Pakil', 'Pangil', 'Paete', 'Luisiana', 'Rizal', 'Calauan', 'Alaminos'])
        province = 'Laguna'
        region = 'CALABARZON'
        address = f"{house_number}, {street}, {barangay}, {city}, {province}, {region}"
        
        try:
            # Health condition (required - create default if none)
            if random.random() < 0.3:  # 30% chance of having specific health condition
                health_type = random.choice(['Mental', 'Physical', 'Chronic'])
                health_condition = fake.text(max_nb_chars=200)
            else:
                health_type = 'None'
                health_condition = 'No known health conditions'
                
            cursor.execute("""
                INSERT INTO missing_person_health_condition (first_name, middle_name, last_name, health_type, health_condition)
                VALUES (%s, %s, %s, %s, %s)
            """, (first_name, middle_name, last_name, health_type, health_condition))
            health_condition_id = cursor.lastrowid
            
            # Insert missing person information
            cursor.execute("""
                INSERT INTO missing_person_information (
                    health_condition_id, first_name, middle_name, last_name, suffix, nickname, gender,
                    date_of_birth, civil_status, citizenship, contact_number, height,
                    weight, hair_color, eye_color, distinguishing_mark, occupation,
                    address, house_number, street, barangay, city, province, region
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (health_condition_id, first_name, middle_name, last_name, suffix, nickname, gender,
                  date_of_birth, civil_status, citizenship, contact_number, height,
                  weight, hair_color, eye_color, distinguishing_mark, occupation,
                  address, house_number, street, barangay, city, province, region))
            
            person_id = cursor.lastrowid
            
            # Create missing person media
            cursor.execute("""
                INSERT INTO missing_person_media (missing_person_id, missing_filename, missing_filetype, missing_filedata, uploaded_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (person_id, 'placeholder.jpg', 'image/jpeg', b'fake_image_data', datetime.now()))
            
            media_id = cursor.lastrowid
            
            # Create location with Laguna, Philippines coordinates
            latitude = random.uniform(14.0, 14.6)  # Laguna latitude range
            longitude = random.uniform(121.0, 121.8)  # Laguna longitude range
            
            cursor.execute("""
                INSERT INTO missing_person_location (location)
                VALUES (ST_GeomFromText(%s))
            """, (f'POINT({longitude} {latitude})',))
            
            location_id = cursor.lastrowid
            
            # Create last seen information
            date_last_seen = fake.date_between(start_date='-30d', end_date='today')
            time_last_seen = fake.time()
            clothing_description = fake.text(max_nb_chars=200)
            circumstances = fake.text(max_nb_chars=300)
            
            cursor.execute("""
                INSERT INTO missing_person_last_seen (
                    person_id, missing_person_location_id, date_last_seen, time_last_seen,
                    clothing_description, circumstances
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (person_id, location_id, date_last_seen, time_last_seen,
                  clothing_description, circumstances))
            
            last_seen_id = cursor.lastrowid
            
            # Create case file - distribute across 12 months
            month = months[i % 12]  # Distribute evenly across 12 months
            year = random.choice([2023, 2024])
            day = random.randint(1, 28)  # Safe day for all months
            submitted_at = datetime(year, month, day, random.randint(0, 23), random.randint(0, 59))
            
            cursor.execute("""
                INSERT INTO case_file (
                    reporter_type, reporter_id, approval_status, case_status, priority,
                    date_and_time_reported, last_updated, notes, last_seen_id, media_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, ('user', user_id, 'pending', 'Open', 'medium', submitted_at, submitted_at,
                  '', last_seen_id, media_id))
            
            print(f"Created missing person report {i+1}: {first_name} {last_name}")
            
        except Exception as e:
            print(f"Error creating missing person report {i+1}: {e}")
            print(f"Data: {first_name}, {middle_name}, {last_name}")
            conn.rollback()
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Successfully created {count} missing person reports")

def main():
    print("Starting data generation...")
    
    print("\n1. Creating 20 fake users...")
    create_fake_users(20)
    
    print("\n2. Creating 20 fake police officers (distributed across 12 months)...")
    create_fake_police_officers(20)
    
    print("\n3. Creating 20 missing person reports...")
    create_missing_person_reports(20)
    
    print("\nData generation completed!")
    print("\nDefault passwords:")
    print("- Users: password123")
    print("- Police Officers: their badge number (e.g., PO0001)")
    print("\nNote: Missing person reports are linked to the created users")
    print("Police officers are distributed across all 12 months based on date_joined")

if __name__ == "__main__":
    main()