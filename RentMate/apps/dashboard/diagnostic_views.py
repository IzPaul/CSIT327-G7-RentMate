from django.http import HttpResponse
from django.db import connection
from django.contrib.auth.decorators import login_required


@login_required
def check_database_schema(request):
    """Diagnostic view to check MonthlyBilling table schema"""
    html = ['<html><head><title>Database Schema Check</title></head><body>']
    html.append('<h1>MonthlyBilling Table Schema</h1>')
    
    try:
        with connection.cursor() as cursor:
            # Check if table exists and get column info
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'dashboard_monthlybilling'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            
            if columns:
                html.append('<table border="1" cellpadding="5" cellspacing="0">')
                html.append('<tr><th>Column Name</th><th>Data Type</th><th>Nullable</th><th>Default</th></tr>')
                for col_name, col_type, nullable, default in columns:
                    html.append(f'<tr><td><strong>{col_name}</strong></td><td>{col_type}</td><td>{nullable}</td><td>{default or "None"}</td></tr>')
                html.append('</table>')
            else:
                html.append('<p style="color: red;">Table dashboard_monthlybilling does not exist</p>')
                
    except Exception as e:
        html.append(f'<p style="color: red;">Error: {str(e)}</p>')
    
    html.append('</body></html>')
    return HttpResponse('\n'.join(html))
