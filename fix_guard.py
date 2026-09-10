with open('frontend/src/layout/index.vue', 'r', encoding='utf-8') as f:
    code = f.read()

import re
old_guard = r"if \(r === 'TEAM_LEADER' && route\.path !== '/dashboard'\) router\.push\('/dashboard'\)"
new_guard = "if (r === 'TEAM_LEADER' && !['/dashboard', '/report/production', '/report/overtime', '/grading'].includes(route.path)) router.push('/dashboard')"

code = re.sub(old_guard, new_guard, code)

with open('frontend/src/layout/index.vue', 'w', encoding='utf-8') as f:
    f.write(code)
