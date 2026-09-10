with open('frontend/src/router/index.ts', 'r', encoding='utf-8') as f:
    code = f.read()

new_routes = '''      {
        path: '/report/production',
        name: 'ProductionReport',
        component: () => import('@/views/report/production.vue'),
        meta: { title: '生产报表', requiresAuth: true }
      },
      {
        path: '/report/overtime',
        name: 'OvertimeReport',
        component: () => import('@/views/report/overtime.vue'),
        meta: { title: '加班报表', requiresAuth: true }
      },
      {
        path: '/grading',
        name: 'DailyGrading',
        component: () => import('@/views/grading/index.vue'),
        meta: { title: '员工日考评', requiresAuth: true }
      },'''

code = code.replace("      {", new_routes + "\n      {", 1)
with open('frontend/src/router/index.ts', 'w', encoding='utf-8') as f:
    f.write(code)
