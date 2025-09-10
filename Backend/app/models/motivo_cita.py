from app import db

class MotivoCita(db.Model):
    __tablename__ = 'motivo_cita'
    id      = db.Column(db.Integer, primary_key=True)
    motivo  = db.Column(db.String(120), unique=True, nullable=False)
    id_area = db.Column(db.Integer, db.ForeignKey('areas.id_area'), nullable=False)

    area_rel = db.relationship('Area', back_populates='motivos')

    def to_dict(self):
        return {
            "id": self.id,
            "motivo": self.motivo,
            "id_area": self.id_area,
            "area": self.area_rel.area if self.area_rel else None
        }
