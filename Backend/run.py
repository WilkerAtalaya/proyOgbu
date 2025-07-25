from app import db, create_app
from sqlalchemy import text

app = create_app()

with app.app_context():
    result = db.session.execute(text("SELECT 1"))
    print("✅ Conexión exitosa:", result.scalar())


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

