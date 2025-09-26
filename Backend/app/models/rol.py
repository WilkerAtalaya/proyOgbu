from app import db

class Rol(db.Model):
    __tablename__ = 'roles'

    id_rol = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id_area'), nullable=True)
    area = db.relationship('Area')

    usuarios = db.relationship('Usuario', back_populates='rol_rel', lazy='dynamic')

    def to_dict(self):
        return {
            "id_rol": self.id_rol,
            "slug": self.slug,
            "nombre": self.nombre,
            "area_id": self.area_id,
            "area": self.area.area if self.area else None
        }
