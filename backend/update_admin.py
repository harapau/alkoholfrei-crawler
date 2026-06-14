#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

admin_file = r"c:\Users\maral\Documents\GitHub\alkoholfrei-crawler\backend\app\routes\admin.py"

with open(admin_file, 'r', encoding='utf-8') as f:
    code = f.read()

new_route = '''
@bp.route('/database/clear', methods=['POST'])
def clear_database():
    """Lösche alle Weine aus der Datenbank."""
    try:
        from app.models.wine import Wine
        from app import db
        count = Wine.query.delete()
        db.session.commit()
        return jsonify({
            "message": f"Datenbank geleert: {count} Wein(e) gelöscht.",
        }), 200
    except Exception as exc:
        current_app.logger.exception('Fehler beim Löschen der Datenbank')
        return jsonify({
            "error": "Fehler beim Löschen der Datenbank.",
            "detail": str(exc),
        }), 500
'''

with open(admin_file, 'w', encoding='utf-8') as f:
    f.write(code.rstrip() + '\n' + new_route)

print('✅ admin.py aktualisiert mit /database/clear route')
