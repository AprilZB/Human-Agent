with open('backend/app/api/production.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_logic = '''        date_str = request.args.get('date')
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                query = query.filter(
                    BizWorkOrder.created_at >= datetime.combine(target_date, datetime.min.time()),
                    BizWorkOrder.created_at <= datetime.combine(target_date, datetime.max.time())
                )
            except ValueError:
                pass'''

new_logic = '''        date_str = request.args.get('date')
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                query = query.join(BizProductionOrder).filter(
                    BizProductionOrder.plan_start_time >= datetime.combine(target_date, datetime.min.time()),
                    BizProductionOrder.plan_start_time <= datetime.combine(target_date, datetime.max.time())
                )
            except ValueError:
                pass'''

if 'query = query.join(BizProductionOrder).filter(' not in code:
    code = code.replace(old_logic, new_logic)
    with open('backend/app/api/production.py', 'w', encoding='utf-8') as f:
        f.write(code)
        
