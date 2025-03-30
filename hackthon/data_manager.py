from database import db, TenderDocument
import json

class TenderDataManager:
    def save_tender_data(self, tender_data, generated_content):
        try:
            tender_doc = TenderDocument(
                tender_id=tender_data['tender_id'],
                tender_title=tender_data['tender_title'],
                issuing_authority=tender_data['issuing_authority'],
                tender_amount=tender_data['tender_amount'],
                bid_start_date=tender_data['bid_start_date'],
                bid_end_date=tender_data['bid_end_date'],
                eligibility_criteria=tender_data['eligibility_criteria'],
                scope_of_work=tender_data['scope_of_work'],
                requirements=tender_data['requirements'],
                contact_details=tender_data['contact_details'],
                mvp_details=tender_data['mvp_details'],
                milestone_deliverables=tender_data['milestone_deliverables'],
                liquidated_damages=tender_data['liquidated_damages']
            )
            
            if generated_content:
                tender_doc.generated_content = json.dumps(generated_content)
            
            db.session.add(tender_doc)
            db.session.commit()
            return tender_doc
            
        except Exception as e:
            db.session.rollback()
            raise e