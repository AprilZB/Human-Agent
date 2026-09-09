import sys

with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "df = pd.DataFrame(data)" in line:
        new_lines.append("        if not data:\n")
        new_lines.append("            cols = [c.name for c in model.__table__.columns if c.name not in ['id', 'created_at']]\n")
        new_lines.append("            df = pd.DataFrame(columns=cols)\n")
        new_lines.append("        else:\n")
        new_lines.append("            df = pd.DataFrame(data)\n")
    else:
        new_lines.append(line)

with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
