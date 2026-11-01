import sqlite3
from database import get_connection, init_db

def seed_blowers():
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM equipment")
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    assemblies = [
        'Carburetor & Fuel System',
        'Ignition & Electrical',
        'Air Filtration & Intake',
        'Exhaust & Spark Arrestor',
        'Recoil Starter & Shrouds',
        'Valve Train & Head'
    ]
    asm_ids = {}
    for name in assemblies:
        cur.execute("INSERT OR IGNORE INTO assemblies (name) VALUES (?)", (name,))
        cur.execute("SELECT id FROM assemblies WHERE name = ?", (name,))
        asm_ids[name] = cur.fetchone()[0]

    models = [
        (
            'Blowers', 'Stihl', 'BR 600 Magnum',
            'https://images.unsplash.com/photo-1590856029826-c7a73142bbf1?w=200&h=200&fit=crop',
            '50:1 Synthetic Mix (Stihl HP Ultra)', 'None (4-MIX fuel lubed)',
            '50:1 with 89+ Octane Unleaded', 'NGK CMR6H (0.020 in / 0.5 mm gap)',
            '0.10 mm (0.004 in) Intake & Exhaust (Cold at TDC)',
            'Standard commercial fleet workhorse. 4-MIX engine requires periodic valve adjustment.'
        ),
        (
            'Blowers', 'Stihl', 'BR 700',
            'https://images.unsplash.com/photo-1590856029826-c7a73142bbf1?w=200&h=200&fit=crop',
            '50:1 Synthetic Mix (Stihl HP Ultra)', 'None (4-MIX fuel lubed)',
            '50:1 with 89+ Octane Unleaded', 'NGK CMR6H (0.020 in / 0.5 mm gap)',
            '0.10 mm (0.004 in) Intake & Exhaust (Cold at TDC)',
            'High-CFM blower. Uses identical powerhead & valve train specs as BR 600.'
        ),
        (
            'Blowers', 'Stihl', 'BR 800 C-E Magnum',
            'https://images.unsplash.com/photo-1590856029826-c7a73142bbf1?w=200&h=200&fit=crop',
            '50:1 Synthetic Mix (Stihl HP Ultra)', 'None (4-MIX fuel lubed)',
            '50:1 with 89+ Octane Unleaded', 'NGK CMR6H (0.020 in / 0.5 mm gap)',
            '0.10 mm (0.004 in) Intake & Exhaust (Cold at TDC)',
            'Heavy-duty 79.9cc. Features side-start pull rope mechanism.'
        )
    ]

    model_ids = {}
    for cat, make, model, img, oil, cap, fuel, plug, valve, notes in models:
        cur.execute("""
            INSERT INTO equipment (category, make, model, image_url, oil_type, oil_capacity, fuel_mix, spark_plug_spec, valve_spec, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cat, make, model, img, oil, cap, fuel, plug, valve, notes))
        model_ids[model] = cur.lastrowid

    cur.execute("INSERT INTO fleet_units (equipment_id, unit_tag, status, notes) VALUES (?, 'BP-01', 'In Service', 'Primary trailer rack unit')", (model_ids['BR 600 Magnum'],))
    cur.execute("INSERT INTO fleet_units (equipment_id, unit_tag, status, notes) VALUES (?, 'BP-02', 'In Service', 'Secondary trailer backup')", (model_ids['BR 600 Magnum'],))
    cur.execute("INSERT INTO fleet_units (equipment_id, unit_tag, status, notes) VALUES (?, 'BP-03', 'In Service', 'Fall clean-up high CFM unit')", (model_ids['BR 700'],))

    parts_data = [
        ('NGK CMR6H Spark Plug', 'Stihl 0000 400 7011 / NGK 3365', '10mm thread, 0.020" gap', 'Drawer: H-01', 12, 4, 'Dealer', 'https://www.stihlusa.com', ['Ignition & Electrical'], ['BR 600 Magnum', 'BR 700', 'BR 800 C-E Magnum']),
        ('BR 600 / 700 Pleated Air Filter', 'Stihl 4282 141 0300', 'Pleated paper cartridge', 'Rack: B-01', 4, 2, 'Stens', 'https://www.hlsproparts.com', ['Air Filtration & Intake'], ['BR 600 Magnum', 'BR 700']),
        ('Zama GND-88 Diaphragm & Gasket Kit', 'Stihl 4282 007 1061', 'Carb metering diaphragm', 'Drawer: H-04', 6, 2, 'HL Supply', 'https://www.hlsproparts.com', ['Carburetor & Fuel System'], ['BR 600 Magnum', 'BR 700']),
        ('In-Tank Felt Fuel Pickup Filter', 'Stihl 0000 350 3502', 'Felt pickup body', 'Drawer: H-05', 8, 3, 'Stens', 'https://www.stens.com', ['Carburetor & Fuel System'], ['BR 600 Magnum', 'BR 700', 'BR 800 C-E Magnum']),
        ('Spark Arrestor Exhaust Screen', 'Stihl 4282 140 6900', 'Fine stainless screen', 'Drawer: H-07', 4, 2, 'Dealer', 'https://www.stihlusa.com', ['Exhaust & Spark Arrestor'], ['BR 600 Magnum', 'BR 700']),
        ('Starter Rope #4.5 (3.5mm)', 'Stihl 0000 195 8200', 'Solid braided cord', 'Rack: A-01', 50, 10, 'Dealer', 'https://www.stihlusa.com', ['Recoil Starter & Shrouds'], ['BR 600 Magnum', 'BR 700']),
        ('Valve Cover Gasket', 'Stihl 4282 029 0500', 'Rocker cover seal', 'Drawer: H-08', 3, 1, 'Dealer', 'https://www.stihlusa.com', ['Valve Train & Head'], ['BR 600 Magnum', 'BR 700', 'BR 800 C-E Magnum'])
    ]

    for name, oem, spec, loc, qty, min_q, supp, url, target_asms, target_models in parts_data:
        cur.execute("""
            INSERT INTO parts (name, oem_number, hardware_spec, location, stock_qty, reorder_min, supplier_name, reorder_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, oem, spec, loc, qty, min_q, supp, url))
        part_id = cur.lastrowid

        for m_name in target_models:
            eq_id = model_ids[m_name]
            for a_name in target_asms:
                asm_id = asm_ids[a_name]
                cur.execute("""
                    INSERT INTO equipment_parts (equipment_id, assembly_id, part_id)
                    VALUES (?, ?, ?)
                """, (eq_id, asm_id, part_id))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    seed_blowers()
