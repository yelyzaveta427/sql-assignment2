import uuid
import random
from datetime import datetime, timedelta

import psycopg2
from psycopg2.extras import execute_values
from faker import Faker


# Connection settings
HOST = 'localhost' # put your credentials here
USER = 'postgres' # put your credentials here
PASSWORD = 'chocko777elza' # put your credentials here
DATABASE = 'hospital' # put your credentials here
PORT = '5432' # put your credentials here

# Data volume settings
PATIENT_COUNT = 10_000
DOCTOR_COUNT = 10_000
APPOINTMENT_COUNT = 10_000
CHUNK_SIZE = 10_000

fake = Faker()


def insert_patients(cursor):
    print("Inserting into patients...")

    client_insert_query = """
        INSERT INTO patients
            (patient_id, patient_name, patient_phone, patient_age)
        VALUES %s
    """

    patient_ids = []

    for start in range(0, PATIENT_COUNT, CHUNK_SIZE):
        current_chunk_size = min(CHUNK_SIZE, PATIENT_COUNT - start)

        patients_data = []
        for _ in range(current_chunk_size):
            patient_id = str(uuid.uuid4())
            patient_ids.append(patient_id)

            patients_data.append(
                (
                    patient_id,
                    fake.name(),
                    fake.phone_number(),
                    random.randint(1, 90)
                )
            )

        execute_values(cursor, client_insert_query, patients_data)
        print(f"Inserted {start + current_chunk_size} rows into patients...")

    print("Inserted into patients.")
    return patient_ids


def insert_doctors(cursor):
    print("Inserting into doctors...")

    doctor_insert_query = """
        INSERT INTO doctors
            (doctor_name, doctor_phone, specialization)
        VALUES %s
        RETURNING doctor_id
    """

    specializations = ["Therapist", "Pediatrician", "Cardiologist", "Neurologist", "Psychiatrist"]

    doctors_data = [
        (
            fake.name(),
            fake.phone_number(),
            random.choice(specializations),
        )
        for _ in range(DOCTOR_COUNT)
    ]

    execute_values(cursor, doctor_insert_query, doctors_data)
    doctor_ids = [row[0] for row in cursor.fetchall()]

    print("Inserted into doctors.")
    return doctor_ids


def insert_appointments(cursor, patient_ids, doctor_ids):

    print("Inserting into appointments...")

    appointment_insert_query = """
        INSERT INTO appointments
            (appointment_date, patient_id, doctor_id, diagnosis, status, cost)
        VALUES %s
    """
    cursor.execute("SELECT doctor_id, specialization FROM doctors;")
    doctor_specializations = {row[0]: row[1] for row in cursor.fetchall()}
    appointment_date_start = datetime.now() - timedelta(days=365 * 5)
    diagnoses_for_every_doctor = {
        "Therapist": ["Flu", "Acute Bronchitis", "Gastritis", "Fatigue"],
        "Pediatrician": ["Chickenpox", "Tonsillitis", "Measles", "Otitis Media"],
        "Cardiologist": ["Hypertension", "Arrhythmia", "Ischemic Heart Disease", "Heart Failure"],
        "Neurologist": ["Migraine", "Sciatica", "Epilepsy", "Insomnia"],
        "Psychiatrist": ["Anxiety Disorder", "Depression", "Panic Attacks", "Bipolar Disorder"]
    }
    price_list = {
        "Therapist": 500,
        "Pediatrician": 600,
        "Cardiologist": 900,
        "Neurologist": 850,
        "Psychiatrist": 1000
    }

    appointment_statuses = ["Completed", "Canceled", "In progress"]
    for start in range(0, APPOINTMENT_COUNT, CHUNK_SIZE):
        current_chunk_size = min(CHUNK_SIZE, APPOINTMENT_COUNT - start)
        appointments_data = []
        for _ in range(current_chunk_size):
            random_doctor_id = random.choice(doctor_ids)
            spec = doctor_specializations[random_doctor_id]
            random_diagnosis = random.choice(diagnoses_for_every_doctor[spec])
            visit_status = random.choice(appointment_statuses)
            cost_of_visit = price_list[spec]
            appointments_data.append(
                (
                    appointment_date_start + timedelta(days=random.randint(0, 365 * 5)),
                    random.choice(patient_ids),
                    random_doctor_id,
                    random_diagnosis,
                    visit_status,
                    cost_of_visit
                )
            )

        execute_values(cursor, appointment_insert_query, appointments_data)
        print(f"Inserted {start + current_chunk_size} rows into appointments...")

    print("Inserted into appointments.")


def main():
    connection = psycopg2.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        dbname=DATABASE,
        port=PORT,
    )

    try:
        with connection:
            with connection.cursor() as cursor:
                patient_ids = insert_patients(cursor)
                doctor_ids = insert_doctors(cursor)
                insert_appointments(cursor, patient_ids, doctor_ids)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
