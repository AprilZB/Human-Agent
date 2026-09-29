with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

import_logic = '''        else:
            # Generic aggregation to prevent duplicate PKs in the same excel file
            pk_name = model.__table__.primary_key.columns.keys()[0]
            agg_dict = {}
            for rec in records:
                pval = rec.get(pk_name)
                if pval is not None:
                    agg_dict[pval] = rec
            records = list(agg_dict.values())'''

new_import_logic = '''        else:
            # Generic aggregation to prevent duplicate PKs in the same excel file
            pk_names = model.__table__.primary_key.columns.keys()
            agg_dict = {}
            for rec in records:
                # Composite key support
                pval = tuple(rec.get(pk) for pk in pk_names)
                # Only aggregate if all parts of the primary key are present
                if all(p is not None for p in pval):
                    agg_dict[pval] = rec
            records = list(agg_dict.values())'''

code = code.replace(import_logic, new_import_logic)
with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
    f.write(code)
