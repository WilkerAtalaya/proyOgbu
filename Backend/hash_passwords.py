from app import create_app, db
from app.models.usuarios import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    usuarios = Usuario.query.all()
    for usuario in usuarios:
        if not usuario.contraseña.startswith("pbkdf2:sha256:"):
            nueva_hash = generate_password_hash(usuario.contraseña, method='pbkdf2:sha256')
            print(f"↪ Hasheando: {usuario.correo} -> {nueva_hash}")
            usuario.contraseña = nueva_hash
    db.session.commit()
    print("✅ Contraseñas actualizadas con pbkdf2:sha256")
