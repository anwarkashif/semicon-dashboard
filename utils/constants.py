# --- Comprehensive Global ISO-3 & Regional Dictionary ---
COUNTRY_INFO = {
    "United States": ("USA", "Americas"), "USA": ("USA", "Americas"), "US": ("USA", "Americas"), "U.S.": ("USA", "Americas"),
    "Canada": ("CAN", "Americas"), "Mexico": ("MEX", "Americas"), "Brazil": ("BRA", "Americas"), "Argentina": ("ARG", "Americas"),
    "Chile": ("CHL", "Americas"), "Colombia": ("COL", "Americas"), "Peru": ("PER", "Americas"), "Venezuela": ("VEN", "Americas"), "Cuba": ("CUB", "Americas"),
    "United Kingdom": ("GBR", "Europe"), "UK": ("GBR", "Europe"), "U.K.": ("GBR", "Europe"), "Britain": ("GBR", "Europe"),
    "Germany": ("DEU", "Europe"), "France": ("FRA", "Europe"), "Italy": ("ITA", "Europe"), "Spain": ("ESP", "Europe"),
    "Netherlands": ("NLD", "Europe"), "Belgium": ("BEL", "Europe"), "Switzerland": ("CHE", "Europe"), "Poland": ("POL", "Europe"),
    "Sweden": ("SWE", "Europe"), "Norway": ("NOR", "Europe"), "Denmark": ("DNK", "Europe"), "Finland": ("FIN", "Europe"),
    "Ireland": ("IRL", "Europe"), "Russia": ("RUS", "Europe"), "Ukraine": ("UKR", "Europe"), "European Union": ("EU", "Europe"), "EU": ("EU", "Europe"),
    "Iran": ("IRN", "West Asia/Middle East"), "Israel": ("ISR", "West Asia/Middle East"), "Saudi Arabia": ("SAU", "West Asia/Middle East"),
    "United Arab Emirates": ("ARE", "West Asia/Middle East"), "UAE": ("ARE", "West Asia/Middle East"), "Qatar": ("QAT", "West Asia/Middle East"),
    "Oman": ("OMN", "West Asia/Middle East"), "Kuwait": ("KWT", "West Asia/Middle East"), "Bahrain": ("BHR", "West Asia/Middle East"),
    "Syria": ("SYR", "West Asia/Middle East"), "Iraq": ("IRQ", "West Asia/Middle East"), "Jordan": ("JOR", "West Asia/Middle East"),
    "Lebanon": ("LBN", "West Asia/Middle East"), "Yemen": ("YEM", "West Asia/Middle East"), "Turkey": ("TUR", "West Asia/Middle East"),
    "China": ("CHN", "Asia"), "Taiwan": ("TWN", "Asia"), "Japan": ("JPN", "Asia"), "South Korea": ("KOR", "Asia"), "North Korea": ("PRK", "Asia"),
    "India": ("IND", "Asia"), "Pakistan": ("PAK", "Asia"), "Bangladesh": ("BGD", "Asia"), "Sri Lanka": ("LKA", "Asia"),
    "Vietnam": ("VNM", "Asia"), "Malaysia": ("MYS", "Asia"), "Singapore": ("SGP", "Asia"), "Indonesia": ("IDN", "Asia"),
    "Philippines": ("PHL", "Asia"), "Thailand": ("THA", "Asia"), "Myanmar": ("MMR", "Asia"), "Cambodia": ("KHM", "Asia"),
    "South Africa": ("ZAF", "Africa"), "Egypt": ("EGY", "Africa"), "Nigeria": ("NGA", "Africa"), "Kenya": ("KEN", "Africa"),
    "Ethiopia": ("ETH", "Africa"), "Morocco": ("MAR", "Africa"), "Algeria": ("DZA", "Africa"), "Sudan": ("SDN", "Africa"),
    "Congo": ("COD", "Africa"), "Democratic Republic of the Congo": ("COD", "Africa"), "Angola": ("AGO", "Africa"), "Ghana": ("GHA", "Africa"),
    "Mali": ("MLI", "Africa"), "Niger": ("NER", "Africa"), "Chad": ("TCD", "Africa"), "Somalia": ("SOM", "Africa"),
    "Australia": ("AUS", "Oceania"), "New Zealand": ("NZL", "Oceania"), "Fiji": ("FJI", "Oceania"), "Papua New Guinea": ("PNG", "Oceania")
}

INFRASTRUCTURE_DATA = {
    "Semiconductor Fabs": [
        {"name": "TSMC - Gigafab 12 (Hsinchu, Taiwan)", "lat": 24.773, "lon": 121.011},
        {"name": "TSMC - Gigafab 18 (Tainan, Taiwan)", "lat": 23.113, "lon": 120.273},
        {"name": "TSMC - JASM (Kumamoto, Japan)", "lat": 32.883, "lon": 130.866},
        {"name": "TSMC - Fab 21 (Phoenix, USA)", "lat": 33.805, "lon": -112.148},
        {"name": "Samsung - Pyeongtaek Campus (South Korea)", "lat": 37.036, "lon": 127.042},
        {"name": "Samsung - Austin Fab (USA)", "lat": 30.368, "lon": -97.625},
        {"name": "Samsung - Taylor Fab [Under Construction] (USA)", "lat": 30.565, "lon": -97.409},
        {"name": "Intel - Ocotillo Campus (Chandler, USA)", "lat": 33.262, "lon": -111.862},
        {"name": "Intel - Ronler Acres (Hillsboro, USA)", "lat": 45.542, "lon": -122.923},
        {"name": "Intel - Fab 34 (Leixlip, Ireland)", "lat": 53.374, "lon": -6.502},
        {"name": "Intel - Magdeburg [Planned] (Germany)", "lat": 52.120, "lon": 11.627},
        {"name": "SMIC - SN1/SN2 (Shanghai, China)", "lat": 31.205, "lon": 121.597},
        {"name": "SMIC - B1/B2 (Beijing, China)", "lat": 39.805, "lon": 116.505},
        {"name": "GlobalFoundries - Fab 8 (Malta, USA)", "lat": 42.970, "lon": -73.754},
        {"name": "GlobalFoundries - Fab 1 (Dresden, Germany)", "lat": 51.125, "lon": 13.714},
        {"name": "GlobalFoundries - Singapore Campus", "lat": 1.436, "lon": 103.768},
        {"name": "UMC - Fab 12A (Tainan, Taiwan)", "lat": 23.115, "lon": 120.275},
        {"name": "Micron - Boise HQ & Fab (USA)", "lat": 43.535, "lon": -116.140},
        {"name": "Micron - Hiroshima Fab (Japan)", "lat": 34.238, "lon": 132.654},
        {"name": "Texas Instruments - Sherman Campus (USA)", "lat": 33.606, "lon": -96.611},
        {"name": "Tata & PSMC (Dholera)", "lat": 22.245, "lon": 72.195},
        {"name": "CG Power (Sanand) - ACTIVE", "lat": 23.005, "lon": 72.385},
        {"name": "Micron (Sanand) - ACTIVE", "lat": 22.956, "lon": 72.338},
        {"name": "Tower Semi (Panvel) - PLANNED", "lat": 18.989, "lon": 73.117},
        {"name": "ASML HQ (Netherlands)", "lat": 51.405, "lon": 5.405},
        {"name": "HIPSPL (3DGS) - 3D Glass Packaging (Odisha, India)", "lat": 20.238, "lon": 85.702}
    ],
    "Critical Mineral Sites": [
        {"name": "Bayan Obo Mine [Largest REE] (China)", "lat": 41.796, "lon": 109.972},
        {"name": "Mountain Pass Mine [REE] (USA)", "lat": 35.473, "lon": -115.527},
        {"name": "Mount Weld Mine [REE] (Australia)", "lat": -28.775, "lon": 122.569},
        {"name": "Salar de Atacama [Lithium Triangle] (Chile)", "lat": -23.500, "lon": -68.250},
        {"name": "Mutanda Mine [Cobalt/Copper] (DRC)", "lat": -10.835, "lon": 25.795},
        {"name": "Kola Peninsula [Nickel/REE] (Russia)", "lat": 67.883, "lon": 33.000},
        {"name": "Manavalakurichi [Monazite (REEs)] (India)", "lat": 8.13, "lon": 77.30},
        {"name": "Chavara (Kollam) [REEs, Titanium] (India)", "lat": 9.01, "lon": 76.53}
    ],
    "Maritime Chokepoints": [
        {"name": "Strait of Malacca", "lat": 1.430, "lon": 103.264},
        {"name": "Strait of Hormuz", "lat": 26.566, "lon": 56.250},
        {"name": "Bab el-Mandeb (Red Sea)", "lat": 12.583, "lon": 43.333},
        {"name": "Suez Canal", "lat": 30.583, "lon": 32.333},
        {"name": "Panama Canal", "lat": 9.116, "lon": -79.750},
        {"name": "Taiwan Strait", "lat": 24.800, "lon": 119.900},
        {"name": "Bosphorus Strait", "lat": 41.221, "lon": 29.113}
    ],
    "Gulf FDI & Capital Diplomacy": [
        {"name": "Manara Minerals (Riyadh)", "lat": 24.7136, "lon": 46.6753},
        {"name": "ADQ Global Headquarters (Abu Dhabi)", "lat": 24.4539, "lon": 54.3773},
        {"name": "International Resources Holding (IRH)", "lat": 25.2048, "lon": 55.2708}
    ],
    "Naval Order of Battle & Strategic Bases": [
        {"name": "Naval Station Norfolk (USA)", "lat": 36.936, "lon": -76.326},
        {"name": "Naval Base San Diego (USA)", "lat": 32.673, "lon": -117.122},
        {"name": "Severomorsk (Russia) - Northern Fleet HQ", "lat": 69.070, "lon": 33.416},
        {"name": "US 7th Fleet HQ (Yokosuka, Japan)", "lat": 35.293, "lon": 139.661},
        {"name": "PLAN Southern Theater Command HQ (Zhanjiang, China)", "lat": 21.206, "lon": 110.402},
        {"name": "Andaman & Nicobar Command (India)", "lat": 11.666, "lon": 92.735},
        {"name": "INS Kadamba (Karwar, India)", "lat": 14.760, "lon": 74.137}
    ],
    "Aerospace & Space Force Installations": [
        {"name": "Cape Canaveral SFS / KSC (USA)", "lat": 28.488, "lon": -80.577},
        {"name": "Jiuquan Satellite Launch Center (China)", "lat": 40.960, "lon": 100.298},
        {"name": "Baikonur Cosmodrome (Kazakhstan)", "lat": 45.964, "lon": 63.305},
        {"name": "Satish Dhawan Space Centre (Sriharikota, India)", "lat": 13.719, "lon": 80.230}
    ]
}