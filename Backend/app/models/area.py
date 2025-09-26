from app import db

class Area(db.Model):
    __tablename__ = 'areas'
    id_area = db.Column(db.Integer, primary_key=True)
    area    = db.Column(db.String(100), unique=True, nullable=False)

    motivos = db.relationship('MotivoCita', back_populates='area_rel', lazy='dynamic')
    roles = db.relationship('Rol', backref='area_ref', lazy='dynamic')

    def to_dict(self):
        return {"id_area": self.id_area, "area": self.area}
