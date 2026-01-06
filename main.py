import os
import time
import random
import pandas as pd
import smtplib
from email.message import EmailMessage
from typing import TypedDict, List
from playwright.sync_api import sync_playwright
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END


from config import (
    GROQ_API_KEY, INPUT_FILE, OUTPUT_FILE, 
    EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER, SMTP_SERVER, SMTP_PORT
)
from browser_utils import create_browser
from ranking_engine import get_organic_rank, get_local_pack_rank

class AgentState(TypedDict):
    keywords: List[str]
    urls: List[str]
    current_index: int
    results: List[dict]

# Shared Globals
PAGE_OBJ = None
BROWSER_OBJ = None


def search_node(state: AgentState):
    idx = state['current_index']
    kw = state['keywords'][idx]
    target = state['urls'][idx]
    print(f"\n [{idx+1}/{len(state['keywords'])}] Analyzing: {kw}")
    
    org = get_organic_rank(PAGE_OBJ, kw, target)
    loc = "Captcha" if org == "Captcha" else ("Network Error" if org == "Network Error" else get_local_pack_rank(PAGE_OBJ, kw))
    
    state['results'].append({
        "Local Keyword Ideas": kw, 
        "Targeted Page": target, 
        "Google Rank (Links)": org, 
        "Google Rank (Places)": loc
    })
    return state


def insight_node(state: AgentState):
    current = state['results'][-1]
    if current['Google Rank (Links)'] in ["Captcha", "Network Error"]:
        state['current_index'] = len(state['keywords'])
        return state

    if not GROQ_API_KEY:
        current['AI Strategic Insight'] = "API Key Missing"
        state['current_index'] += 1
        return state

    try:
        llm = ChatGroq(api_key=GROQ_API_KEY, model_name="llama-3.1-8b-instant", temperature=0.2)
        
        # --- MODIFIED PROMPT BELOW ---
        prompt = PromptTemplate.from_template(
            "Keyword: {kw}\nOrganic Rank: {org}\nLocal Rank: {loc}\n"
            "Business: Omkitchen Noida.\n\n"
            "Task: Provide one SEO tip in exactly 3 short bullet points.\n"
            "Constraint 1: Use a simple hyphen (-) for bullets.\n"
            "Constraint 2: DO NOT use bolding or asterisks (**).\n"
            "Constraint 3: Provide raw text only. No markdown."
        )
        # -----------------------------
        
        chain = prompt | llm
        response = chain.invoke({
            "kw": current['Local Keyword Ideas'],
            "org": current['Google Rank (Links)'],
            "loc": current['Google Rank (Places)']
        })
        
        # Clean up any accidental double asterisks just in case
        clean_content = response.content.strip().replace("**", "")
        current['AI Strategic Insight'] = clean_content
        
        print(f"     AI Verdict: {current['AI Strategic Insight'][:50]}...")
    except Exception as e:
        current['AI Strategic Insight'] = f"Manual Review Needed"
    
    state['current_index'] += 1
    time.sleep(random.uniform(5, 10)) 
    return state

def save_file_node(state: AgentState):
    print("\n Saving results to Excel locally...")
    df_final = pd.DataFrame(state['results'])
    
    with pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter') as writer:
        df_final.to_excel(writer, index=False, sheet_name='Rankings')
        workbook = writer.book
        worksheet = writer.sheets['Rankings']
        box_format = workbook.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
        
        worksheet.set_column('A:A', 25) 
        worksheet.set_column('B:B', 30) 
        worksheet.set_column('C:C', 15) 
        worksheet.set_column('D:D', 15) 
        worksheet.set_column('E:E', 55, box_format)
    
    print(f" Local file saved: {OUTPUT_FILE}")
    return state

def mail_node(state: AgentState):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print(" Email credentials missing. Skipping mail node.")
        return state

    print(f"Sending report to {EMAIL_RECEIVER}...")
    try:
        msg = EmailMessage()
        msg['Subject'] = f"SEO Ranking Report - {time.strftime('%Y-%m-%d')}"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg.set_content(f"Hello,\n\nPlease find the attached SEO Ranking Report for Omkitchen.\n\nKeywords Tracked: {len(state['results'])}\n\nThis is an automated report.")

        with open(OUTPUT_FILE, 'rb') as f:
            msg.add_attachment(
                f.read(),
                maintype='application',
                subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                filename=OUTPUT_FILE
            )

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(" Email sent successfully!")
    except Exception as e:
        print(f" Mail Error: {e}")
    
    return state



workflow = StateGraph(AgentState)
workflow.add_node("search", search_node)
workflow.add_node("insight", insight_node)
workflow.add_node("save_file", save_file_node)
workflow.add_node("mail", mail_node)

workflow.set_entry_point("search")
workflow.add_edge("search", "insight")

#loop through keywords, then save, then mail
workflow.add_conditional_edges(
    "insight", 
    lambda s: "continue" if s['current_index'] < len(s['keywords']) else "process_end", 
    {"continue": "search", "process_end": "save_file"}
)

workflow.add_edge("save_file", "mail")
workflow.add_edge("mail", END)

app = workflow.compile()

# Generate Graph Image
try:
    graph_viz = app.get_graph()
    with open("graph_flow.png", "wb") as f:
        f.write(graph_viz.draw_mermaid_png())
except:
    pass

if __name__ == "__main__":
    try:
        df_raw = pd.read_excel(INPUT_FILE, header=None)
        header_row = 0
        for i, row in df_raw.iterrows():
            if 'Local Keyword Ideas' in [str(x).strip() for x in row.values]:
                header_row = i
                break
        df_in = pd.read_excel(INPUT_FILE, header=header_row).dropna(subset=['Local Keyword Ideas'])
        df_in = df_in[df_in['Local Keyword Ideas'] != 'Local Keyword Ideas']
    except Exception as e:
        print(f" Excel Error: {e}"); exit()

    with sync_playwright() as p:
        BROWSER_OBJ, PAGE_OBJ = create_browser(p)
        initial_state = {
            "keywords": df_in['Local Keyword Ideas'].tolist(), 
            "urls": df_in['Targeted Page'].tolist(), 
            "current_index": 0, 
            "results": []
        }
        
        # This will now run search then insight (loop) then save_file then mail
        final_state = app.invoke(initial_state, config={"recursion_limit": 500})
        
        BROWSER_OBJ.close()
    
    print(f"\n All Done! Results are in {OUTPUT_FILE} and your inbox.")