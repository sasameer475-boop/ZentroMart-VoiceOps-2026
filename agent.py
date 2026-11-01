import os,re,sys
from pathlib import Path
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
load_dotenv()
BASE=Path(__file__).resolve().parents[1]
class Agent:
    def __init__(self,dataset=None):
        self.dataset=Path(dataset or BASE/'dataset').resolve()
        sys.path.insert(0,str(self.dataset))
        from tools.tools import lookup_order,create_ticket
        self.lookup_order=lookup_order;self.create_ticket=create_ticket
        self.history=[];self.order_id=None;self.verified=None;self.attempts=0
        self.sections=[]
        for file in sorted((self.dataset/'kb').glob('*.md')):
            if 'superseded' in file.name:continue
            text=file.read_text(encoding='utf-8')
            parts=re.split(r'(?=^#{1,4}\s|^\[[A-Z][A-Z0-9_-]+\])',text,flags=re.M)
            for part in parts:
                if len(part.strip())>35:self.sections.append((file.name,part.strip()[:2400]))
        self.vectorizer=TfidfVectorizer(ngram_range=(1,2),stop_words='english',sublinear_tf=True)
        self.matrix=self.vectorizer.fit_transform([x[1] for x in self.sections])
    def retrieve(self,q,k=6):
        scores=cosine_similarity(self.vectorizer.transform([q]),self.matrix)[0]
        ids=scores.argsort()[::-1][:k]
        return [{'file':self.sections[i][0],'text':self.sections[i][1],'score':round(float(scores[i]),3)} for i in ids if scores[i]>0]
    def respond(self,message):
        message=str(message).strip()
        if not message:return {'reply':'Please repeat your question.','sources':[]}
        ids=re.findall(r'\b\d{6,}\b',message)
        if ids and ('order' in message.lower() or self.order_id is None):self.order_id=ids[0];self.verified=None;self.attempts=0
        needs_order=bool(re.search(r'\b(my order|track my|where is my|order status|my refund|my cancellation)\b',message,re.I))
        if self.order_id and self.verified is None and (needs_order or self.attempts or ids or re.fullmatch(r'\s*\d{4}(?:\d{2})?\s*',message)):
            proof=re.fullmatch(r'\s*(\d{4}|\d{6})\s*',message)
            if proof:
                result=self.lookup_order(self.order_id,proof.group(1));self.attempts+=1
                if result.get('verified'):self.verified=result
                elif self.attempts>=2:return {'reply':'I could not verify the order after two attempts. For privacy, please contact human support.','sources':[]}
                else:return {'reply':'Verification did not match. Please try once more with your registered phone last four digits or delivery pincode.','sources':[]}
            else:return {'reply':'For your privacy, please provide the registered phone last four digits or six-digit delivery pincode to verify the order.','sources':[]}
        if needs_order and not self.order_id:return {'reply':'Please share your order ID. I will then ask for verification before discussing order details.','sources':[]}
        docs=self.retrieve(message)
        if not docs and not self.verified:return {'reply':'I cannot confirm that from the available ZentroMart documents. I can help connect you with support.','sources':[]}
        context='\n\n'.join(f'[{d["file"]}] {d["text"]}' for d in docs)
        order_context=str({k:v for k,v in (self.verified or {}).items() if k not in {'phone','customer_id','customer_first_name'}}) if self.verified else 'No verified order'
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        system=('You are ZentroMart AI support assistant. Start your first reply by identifying yourself as AI. '
                'Use ONLY provided current company evidence and verified order facts. Never invent policies, promises, refunds, amounts, or dates. '
                'Do not expose unverified order information. Ask one question when needed. Be brief, courteous, and conversational. '
                'If evidence is insufficient, say so. For requests needing human discretion, explain handover is required; do not claim a ticket was created unless tool succeeded. '
                'Dataset reference date is 20 October 2026. Historical support logs are not policy authority.')
        conversation = "\n".join(
            f"{'Customer' if item['role'] == 'user' else 'Assistant'}: {item['content']}"
            for item in self.history[-10:]
        )

        prompt = (
            system + "\nVERIFIED ORDER: " + order_context +
            "\nEVIDENCE:\n" + context +
            "\nCONVERSATION:\n" + conversation +
            "\nCustomer: " + message + "\nAssistant:"
        )

        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
            contents=prompt
        )

        reply = response.text or 'I cannot confirm that from the available documents.'
        self.history.extend([{'role':'user','content':message},{'role':'assistant','content':reply}])
        return {'reply':reply,'sources':[{'file':d['file'],'score':d['score']} for d in docs]}
    def ticket(self,summary):
        if self.order_id and not self.verified:
            return {'created':False,'error':'Order must be verified before order-linked ticket creation.'}
        return self.create_ticket(summary,order_id=self.order_id)