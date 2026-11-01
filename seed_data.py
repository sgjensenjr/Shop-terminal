import sqlite3
import os

DB_FILE = 'shop_terminal.db'

def seed():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            icon TEXT,
            image_url TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            make TEXT,
            model_number TEXT,
            fuel_spec TEXT,
            spark_plug TEXT,
            plug_gap TEXT,
            oil_spec TEXT,
            oil_capacity TEXT,
            valve_lash TEXT,
            diagram_url TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE assemblies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER,
            name TEXT,
            FOREIGN KEY (model_id) REFERENCES models(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assembly_id INTEGER,
            name TEXT,
            oem_number TEXT,
            cross_ref TEXT,
            fits_info TEXT,
            restock_url TEXT,
            FOREIGN KEY (assembly_id) REFERENCES assemblies(id)
        )
    ''')

    # Seed Categories
    cats = [
        ("Blowers", "💨"),
        ("Trimmers & Edgers", "🌿"),
        ("Walk-Behind Mowers", "🚜"),
        ("Zero-Turn Mowers", "⚡"),
        ("Cut-Off Saws", "🪚"),
        ("Compactors & Turf", "🧱")
    ]
    cur.executemany("INSERT INTO categories (name, icon) VALUES (?, ?)", cats)

    # 1. Stihl BR 600 / BR 700 Blower
    cur.execute('''
        INSERT INTO models (category_id, make, model_number, fuel_spec, spark_plug, plug_gap, oil_spec, oil_capacity, valve_lash, diagram_url)
        VALUES (1, 'Stihl', 'BR 600 / BR 700', '50:1 Stihl HP Ultra', 'NGK CMR6H', '0.020 in (0.5 mm)', 'Engine uses 50:1 premix', 'N/A', '0.004 in (0.10 mm) Cold at TDC', 'https://www.partstree.com/models/br-600-stihl-backpack-blower')
    ''')
    br_id = cur.lastrowid
    
    cur.execute("INSERT INTO assemblies (model_id, name) VALUES (?, ?)", (br_id, "Fuel & Intake"))
    br_fuel = cur.lastrowid
    cur.execute("INSERT INTO assemblies (model_id, name) VALUES (?, ?)", (br_id, "Ignition & Electrical"))
    br_ign = cur.lastrowid
    cur.execute("INSERT INTO assemblies (model_id, name) VALUES (?, ?)", (br_id, "Shrouds & Recoil"))
    br_shroud = cur.lastrowid

    cur.executemany('''
        INSERT INTO parts (assembly_id, name, oem_number, cross_ref, fits_info, restock_url) VALUES (?, ?, ?, ?, ?, ?)
    ''', [
        (br_fuel, "Main Air Filter", "4282 141 0300", "Stens 102-851", "Fits BR 500, BR 550, BR 600, BR 700", "https://www.partstree.com/parts/stihl-4282-141-0300"),
        (br_fuel, "In-Tank Fuel Filter (Felt)", "0000 350 3502", "Stens 610-939", "Universal across ALL Stihl Handhelds", "https://www.partstree.com/parts/stihl-0000-350-3502"),
        (br_fuel, "Carb Metering Diaphragm Kit", "4180 007 1061", "Zama GND-88 / Stens 615-585", "Fits 4-MIX Zama carbs (BR 600, FS 91, FC 91)", "https://www.partstree.com/parts/zama-gnd-88"),
        (br_fuel, "Tygon Fuel Line (Bulk)", "3/32 ID x 3/16 OD", "Stens 115-303", "Standard replacement fuel line for 2-stroke/4-MIX", "https://www.amazon.com/dp/B000BO8UD6"),
        (br_ign, "Spark Plug", "NGK CMR6H", "Stens 130-540", "Fits BR 600, 700, 800, FS 91 R, FC 91", "https://www.amazon.com/dp/B000CSIL88"),
        (br_ign, "Ignition Module / Coil", "4282 400 1310", "Rotary 14815", "Fits Stihl BR 500, 550, 600, 700", "https://www.partstree.com/parts/stihl-4282-400-1310"),
        (br_shroud, "Plastic Shroud Screw", "IS-D5x24", "Stihl 9074 478 4475", "Pan-head T27 Torx plastic-threading screw", "https://www.partstree.com/parts/stihl-9074-478-4475"),
        (br_shroud, "Recoil Starter Rope #3.5", "0000 930 2203", "Stens 146-911", "Fits all Stihl blowers and trimmers (3.5 mm)", "https://www.amazon.com/dp/B0038U3TT4")
    ])

    # 2. Stihl FS 91 R / FC 91 (Trimmer / Edger)
    cur.execute('''
        INSERT INTO models (category_id, make, model_number, fuel_spec, spark_plug, plug_gap, oil_spec, oil_capacity, valve_lash, diagram_url)
        VALUES (2, 'Stihl', 'FS 91 R / FC 91', '50:1 Stihl HP Ultra', 'NGK CMR6H', '0.020 in (0.5 mm)', 'Engine uses 50:1 premix', 'N/A', '0.004 in (0.10 mm) Cold at TDC', 'https://www.partstree.com/models/fs-91-r-stihl-string-trimmer')
    ''')
    fs_id = cur.lastrowid
    cur.execute("INSERT INTO assemblies (model_id, name) VALUES (?, ?)", (fs_id, "Carb & Filtration"))
    fs_fuel = cur.lastrowid
    cur.execute("INSERT INTO assemblies (model_id, name) VALUES (?, ?)", (fs_id, "Cutting Head & Drive"))
    fs_drive = cur.lastrowid

    cur.executemany('''
        INSERT INTO parts (assembly_id, name, oem_number, cross_ref, fits_info, restock_url) VALUES (?, ?, ?, ?, ?, ?)
    ''', [
        (fs_fuel, "4-MIX Air Filter", "4180 141 0300", "Stens 102-124", "Fits FS 89, FS 91, FS 111, FC 91, HL 94", "https://www.partstree.com/parts/stihl-4180-141-0300"),
        (fs_fuel, "In-Tank Fuel Filter (Felt)", "0000 350 3502", "Stens 610-939", "Universal across ALL Stihl Handhelds", "https://www.partstree.com/parts/stihl-0000-350-3502"),
        (fs_drive, "AutoCut 26-2 Trimmer Head", "4002 710 2169", "Stens 385-591", "Standard bump head for FS 91 R / FS 94 R", "https://www.amazon.com/dp/B079DDCW8C"),
        (fs_drive, "8-Inch Edger Blade (FC 91)", "4133 713 4101", "Stens 390-040", "Heat treated 8x1 inch arbor edger blade", "https://www.amazon.com/dp/B0018U1IHM")
    ])

    # 3. Exmark Commercial 21 (Walk-Behind)
    cur.execute('''
        INSERT INTO models (category_id, make, model_number, fuel_spec, spark_plug, plug_gap, oil_spec, oil_capacity, valve_lash, diagram_url)
        VALUES (3, 'Exmark', 'Commercial 21 (Honda GXV160)', '87 Octane Ethanol-Free', 'NGK BPR5ES', '0.030 in (0.75 mm)', '10W-30 Motor Oil', '0.69 qt (22 oz)', 'Intake: 0.006 in / Exhaust: 0.008 in', 'https://www.partstree.com/models/ecx160chn21000-exmark-21-commercial-walk-behind-mower')
    ''')
    ex_id = cur.lastrowid
    cur.execute("INSERT INTO assemblies (model_id, name) VALUES (?, ?)", (ex_id, "Drive & Transmission"))
    ex_drive = cur.lastrowid
    cur.execute("INSERT INTO assemblies (model_id, name) VALUES (?, ?)", (ex_id, "Engine & Service"))
    ex_eng = cur.lastrowid

    cur.executemany('''
        INSERT INTO parts (assembly_id, name, oem_number, cross_ref, fits_info, restock_url) VALUES (?, ?, ?, ?, ?, ?)
    ''', [
        (ex_drive, "Transmission Drive Cable", "116-4340", "Stens 290-927", "Fits Exmark Commercial 21 self-propelled drive", "https://www.partstree.com/parts/exmark-116-4340"),
        (ex_drive, "Blade Brake Clutch Cable", "116-4341", "Exmark 137-4759", "Bail cable to stop/start blade spin", "https://www.partstree.com/parts/exmark-116-4341"),
        (ex_drive, "Wheel Drive Pinion Gear (15T)", "103-5188", "Exmark 136-9111", "Mesh gear inside rear drive wheels", "https://www.partstree.com/parts/exmark-103-5188"),
        (ex_drive, "High-Lift 21 Blade", "116-3769", "Stens 355-303", "Standard 21 inch commercial bagging/lift blade", "https://www.amazon.com/dp/B007X6B022"),
        (ex_eng, "Dual Element Air Filter", "17211-ZE7-W03", "Stens 100-784", "Fits Honda GXV160 vertical-shaft engine", "https://www.partstree.com/parts/honda-17211-ze7-w03")
    ])

    # 4. Exmark Lazer Z 60 (Zero-Turn)
    cur.execute('''
        INSERT INTO models (category_id, make, model_number, fuel_spec, spark_plug, plug_gap, oil_spec, oil_capacity, valve_lash, diagram_url)
        VALUES (4, 'Exmark', 'Lazer Z 60 (Kawasaki FX730V)', '87 Octane Ethanol-Free', 'NGK BPR4ES', '0.030 in (0.75 mm)', '10W-40 Synthetic Blend', '2.1 qt (with filter)', '0.004 - 0.006 in Cold', 'https://www.partstree.com/models/lzs730gka604a1-exmark-lazer-z-s-series-zero-turn-mower-60-deck')
    ''')
    lz_id = cur.lastrowid
    cur.execute("INSERT INTO assemblies (model_id, name) VALUES (?, ?)", (lz_id, "Engine & Hydraulics"))
    lz_eng = cur.lastrowid
    cur.execute("INSERT INTO assemblies (model_id, name) VALUES (?, ?)", (lz_id, "Deck & Brakes"))
    lz_deck = cur.lastrowid

    cur.executemany('''
        INSERT INTO parts (assembly_id, name, oem_number, cross_ref, fits_info, restock_url) VALUES (?, ?, ?, ?, ?, ?)
    ''', [
        (lz_eng, "Engine Oil Filter", "49065-0721", "Wix 51394 / Stens 120-435", "Fits Kawasaki FX691V, FX730V, FR/FS series", "https://www.amazon.com/dp/B000BPEUBW"),
        (lz_eng, "Canister Primary Air Filter", "11013-7044", "Stens 102-805", "Fits Kawasaki FX heavy-duty dual canister", "https://www.partstree.com/parts/kawasaki-11013-7044"),
        (lz_eng, "Fuel Filter (In-Line)", "49019-0027", "Stens 120-562", "Fits 1/4 and 5/16 fuel lines", "https://www.amazon.com/dp/B0018TY304"),
        (lz_deck, "Tire-Scrub Brake Spring", "109-3893", "Exmark 1-633131", "Compression spring for manual tire-lock parking brake", "https://www.partstree.com/parts/exmark-109-3893"),
        (lz_deck, "60 Deck Drive Belt", "109-4113", "Stens 265-202", "Fits Exmark Lazer Z 60 inch UltraCut series", "https://www.partstree.com/parts/exmark-109-4113")
    ])

    # 5. Plate Compactors & Trenchers (Honda GX160 / GX200)
    cur.execute('''
        INSERT INTO models (category_id, make, model_number, fuel_spec, spark_plug, plug_gap, oil_spec, oil_capacity, valve_lash, diagram_url)
        VALUES (6, 'Honda Powered', 'Plate Compactor (GX160 / GX200)', '87 Octane Ethanol-Free', 'NGK BPR6ES', '0.030 in (0.75 mm)', '10W-30 Motor Oil', '0.61 qt (20 oz)', 'Intake: 0.006 in / Exhaust: 0.008 in', 'https://www.partstree.com/models/gx160-ut2-qx2-honda-engine-made-in-thailand-sn-gcbct-1000001')
    ''')
    gx_id = cur.lastrowid
    cur.execute("INSERT INTO assemblies (model_id, name) VALUES (?, ?)", (gx_id, "Engine & Service"))
    gx_eng = cur.lastrowid

    cur.executemany('''
        INSERT INTO parts (assembly_id, name, oem_number, cross_ref, fits_info, restock_url) VALUES (?, ?, ?, ?, ?, ?)
    ''', [
        (gx_eng, "Dual Element Air Filter", "17210-ZE1-822", "Stens 100-012 / Wix 42709", "Fits Honda GX120, GX160, GX200, Compactors, Aerators", "https://www.partstree.com/parts/honda-17210-ze1-822"),
        (gx_eng, "Complete Carburetor", "16100-ZH8-W61", "Stens 520-718", "Fits Honda GX160 5.5HP horizontal engines", "https://www.amazon.com/dp/B00A85H95G"),
        (gx_eng, "Recoil Starter Assembly", "28400-ZH8-013YA", "Stens 150-703", "Standard pull-cord housing for Honda GX160/GX200", "https://www.amazon.com/dp/B005477L56")
    ])

    conn.commit()
    conn.close()
    print("Database seeded with universal parts, cross-references, and schematics successfully!")

if __name__ == '__main__':
    seed()
