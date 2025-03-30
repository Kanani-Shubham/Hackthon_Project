from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TenderDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tender_id = db.Column(db.String(50), unique=True, nullable=False)
    tender_title = db.Column(db.String(200), nullable=False)
    issuing_authority = db.Column(db.String(200), nullable=False)
    tender_amount = db.Column(db.Float, nullable=False)
    bid_start_date = db.Column(db.Date, nullable=False)
    bid_end_date = db.Column(db.Date, nullable=False)
    eligibility_criteria = db.Column(db.Text, nullable=False)
    scope_of_work = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    contact_details = db.Column(db.Text, nullable=False)
    mvp_details = db.Column(db.Text, nullable=False)
    milestone_deliverables = db.Column(db.Text, nullable=False)
    liquidated_damages = db.Column(db.Text, nullable=False)
    pdf_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)