import os
import json
from collections import Counter
from datetime import datetime, timedelta
from huggingface_hub import HfApi

DATA_DIR = "data"

now = datetime.utcnow()

# 1. Anchor to the most recent Friday (or today, if today is Friday)
# In Python, Monday is 0, Friday is 4
days_since_friday = (now.weekday() - 4) % 7
latest_friday = now - timedelta(days=days_since_friday)

# 2. Calculate exactly two weeks (14 days) prior to that Friday
start_friday = latest_friday - timedelta(days=14)

# 3. Format the dates
start_date = start_friday.strftime("%b %d, %Y")
end_date = latest_friday.strftime("%b %d, %Y")

dynamic_timeframe = f"Bi-Weekly Strategic Assessment ({start_date} to {end_date})"

memory = {
    "date": now.strftime("%Y-%m-%d"),
    "timeframe": dynamic_timeframe,
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
# SAVE OUTPUT & SYNC TO HUB
# ==========================================

os.makedirs(DATA_DIR, exist_ok=True)
output_file = f"{DATA_DIR}/geopolitical_memory.json"

with open(output_file, "w") as f:
    json.dump(memory, f, indent=4)

print("Geopolitical Memory Layer Updated Locally.")

# ==========================================
# ☁️ HUGGING FACE PERMANENT RETENTION SYNC
# ==========================================
HF_TOKEN = os.environ.get("HF_TOKEN")
# If running inside a HF Space, SPACE_ID is automatically available in the environment.
# If running via GitHub Actions, explicitly define your repo ID: "username/space-name"
REPO_ID = os.environ.get("SPACE_ID") or "YOUR_HF_USERNAME/YOUR_SPACE_NAME" 

if HF_TOKEN and REPO_ID:
    try:
        api = HfApi()
        print(f"☁️ Uploading {output_file} to permanent storage on {REPO_ID}...")
        api.upload_file(
            path_or_fileobj=output_file,
            path_in_repo=output_file,
            repo_id=REPO_ID,
            repo_type="space",
            token=HF_TOKEN,
            commit_message=f"Auto-sync Memory Layer: {start_date} to {end_date}"
        )
        print("✅ Successfully locked Geopolitical Memory into permanent Hugging Face storage!")
    except Exception as e:
        print(f"❌ Failed to sync to Hub. File is only in temporary memory! Error: {e}")
else:
    print("⚠️ HF_TOKEN or REPO_ID missing. File saved locally but will be lost on container restart.")