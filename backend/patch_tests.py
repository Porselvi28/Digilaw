import os
import glob

override_code = """
from app.dependencies.auth import get_current_active_user
from app.models.user import User

def override_get_current_active_user():
    return User(id=1, email="legacy_admin@digilaw.ai", is_active=True)

app.dependency_overrides[get_current_active_user] = override_get_current_active_user
"""

files = glob.glob("test_*.py") + ["run_e2e_tests.py"]

for file in files:
    with open(file, "r") as f:
        content = f.read()
    
    if "override_get_current_active_user" in content:
        continue # already patched
        
    if "from app.main import app" in content:
        content = content.replace("from app.main import app", "from app.main import app" + override_code)
    
    with open(file, "w") as f:
        f.write(content)
        
print("Patched test files.")
