from pydantic import BaseModel
from datetime import datetime

class NewsletterCampaign(BaseModel):
    id: int
    subject: str
    content: str
    sent_at: datetime

class NewsletterSubscriber(BaseModel):
    id: int
    email: str
    subscribed_at: datetime 