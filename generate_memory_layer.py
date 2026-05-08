import os
import json
from collections import Counter
from datetime import datetime

DATA_DIR = "data"

memory = {
    "date": datetime.utcnow().strftime("%Y-%m-%d"),
    "persistent_patterns": [],
    "strategic_observation": ""
}

all_text = ""

# ==========================================
# LOAD WEEKLY ARCHIVES
# ==========================================

for file in os.listdir(DATA_DIR):
    if file.endswith(".json") and "brief" in file.lower():

        try:
            with open(os.path.join(DATA_DIR, file), "r") as f:
                data = json.load(f)

                raw = data.get("brief_raw", "")
                all_text += " " + raw.lower()

        except:
            pass

# ==========================================
# PATTERN DETECTION
# ==========================================

patterns = []

# Taiwan
taiwan_count = all_text.count("taiwan")
if taiwan_count > 10:
    patterns.append(
        "Taiwan remains a persistent semiconductor vulnerability node."
    )

# Rare Earth
ree_count = all_text.count("rare earth")
if ree_count > 5:
    patterns.append(
        "Rare earth supply chain dependence remains structurally unresolved."
    )

# Export Controls
export_count = all_text.count("export control")
if export_count > 5:
    patterns.append(
        "Export control activity continues to intensify across assessment cycles."
    )

# Military
military_count = all_text.count("military")
if military_count > 8:
    patterns.append(
        "Military-linked semiconductor disruptions show sustained escalation."
    )

# China
china_count = all_text.count("china")
if china_count > 20:
    patterns.append(
        "China remains the dominant geopolitical actor shaping semiconductor risk."
    )

memory["persistent_patterns"] = patterns

# ==========================================
# STRATEGIC OBSERVATION
# ==========================================

if len(patterns) >= 4:
    observation = (
        "Supply chain fragmentation is becoming systemic rather than episodic."
    )
elif len(patterns) >= 2:
    observation = (
        "Geopolitical pressure on semiconductor ecosystems remains elevated."
    )
else:
    observation = (
        "No dominant long-duration structural shift detected."
    )

memory["strategic_observation"] = observation

# ==========================================
# SAVE OUTPUT
# ==========================================

os.makedirs(DATA_DIR, exist_ok=True)

with open(f"{DATA_DIR}/geopolitical_memory.json", "w") as f:
    json.dump(memory, f, indent=4)

print("Geopolitical Memory Layer Updated.")