import sqlite3

DATABASE_NAME = "shop_parts.db"

def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        make TEXT NOT NULL,
        model TEXT NOT NULL,
        image_url TEXT,
        oil_type TEXT,
        oil_capacity TEXT,
        fuel_mix TEXT,
        spark_plug_spec TEXT,
        valve_spec TEXT,
        notes TEXT
    );

    CREATE TABLE IF NOT EXISTS fleet_units (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER NOT NULL,
        unit_tag TEXT UNIQUE NOT NULL,
        serial_number TEXT,
        status TEXT DEFAULT 'In Service',
        notes TEXT,
        FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS assemblies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS parts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        oem_number TEXT,
        hardware_spec TEXT,
        location TEXT NOT NULL,
        stock_qty INTEGER DEFAULT 0,
        reorder_min INTEGER DEFAULT 1,
        supplier_name TEXT,
        reorder_url TEXT
    );

    CREATE TABLE IF NOT EXISTS equipment_parts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER NOT NULL,
        assembly_id INTEGER NOT NULL,
        part_id INTEGER NOT NULL,
        FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
        FOREIGN KEY (assembly_id) REFERENCES assemblies(id) ON DELETE CASCADE,
        FOREIGN KEY (part_id) REFERENCES parts(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS maintenance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unit_id INTEGER NOT NULL,
        service_date DATE DEFAULT (DATE('now')),
        work_performed TEXT NOT NULL,
        parts_used TEXT,
        tech_notes TEXT,
        FOREIGN KEY (unit_id) REFERENCES fleet_units(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
