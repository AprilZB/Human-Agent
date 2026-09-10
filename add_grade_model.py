with open('backend/app/models/production.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_model = '''
class BizEmployeeDailyGrade(Base):
    __tablename__ = 'biz_employee_daily_grade'
    id = Column(Integer, primary_key=True, autoincrement=True)
    grade_date = Column(DATE, nullable=False)
    employee_id = Column(String(50), nullable=False)
    score = Column(Integer, default=0) # -4, -2, 0, 2, 4
    remark = Column(String(255))
    graded_by = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
'''

if 'BizEmployeeDailyGrade' not in code:
    code = code + "\n" + new_model
    with open('backend/app/models/production.py', 'w', encoding='utf-8') as f:
        f.write(code)
