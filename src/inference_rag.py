import sys, os, re
_p = __import__('pathlib').Path(__file__).resolve()
sys.path.insert(0, str(_p.parents[1]))
sys.path.insert(0, str(_p.parent))
import config as cfg
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import chromadb
import os
import time
import numpy as np
import pandas as pd
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# ── XAI module (Tuần 17) ─────────────────────────────────────────────────────
try:
    from xai_shap import (
        explain_recommendation,
        build_background,
        extract_features,
        FEATURE_NAMES,
    )
    XAI_AVAILABLE = True
except ImportError:
    XAI_AVAILABLE = False
    print("[WARN] xai_shap not found — XAI disabled. Run: pip install shap")

app = FastAPI(title="Wine Recommendation API")

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=str(cfg.CHROMA_DB))
collection = chroma_client.get_or_create_collection(name="wine_inventory")

# Global Variables
tokenizer        = None
model            = None
shap_background  = None   # np.ndarray (n_bg, 5) for SHAP KernelExplainer
catalog_df_cache = None   # cached DataFrame for SHAP background builds
catalog_df       = None   # Cached semantic catalog DataFrame

class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    query: str
    history: List[Message] = Field(default_factory=list)
    model_version: int = 1

app.mount("/static", StaticFiles(directory=str(cfg.STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    return FileResponse(cfg.STATIC_DIR / "index.html")

@app.on_event("startup")
def load_models_and_data():
    global tokenizer, model, shap_background, catalog_df_cache, catalog_df

    # ── 1. Populate Vector DB ─────────────────────────────────────────────────
    print("Initializing Vector DB Inventory...")
    try:
        if collection.count() > 0:
            print(f"Vector DB already has {collection.count()} wines. Skipping ingestion.")
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(base_dir, str(cfg.WINE_CSV))
            df = pd.read_csv(csv_path)
            df = df.dropna(subset=["country","variety","description","title","price"]).head(5000)
            docs, metadatas, ids = [], [], []
            for idx, row in df.iterrows():
                docs.append(row["description"])
                metadatas.append({
                    "title"  : row["title"],
                    "country": row["country"],
                    "variety": row["variety"],
                    "price"  : float(row["price"]),
                })
                ids.append(str(idx))
            collection.add(documents=docs, metadatas=metadatas, ids=ids)
            print(f"Loaded {len(ids)} wines into ChromaDB.")
    except Exception as e:
        print(f"[WARN] DB init skipped: {e}")

    # ── 2. Load Fine-Tuned LLM (Llama-3-8B + LoRA) ───────────────────────────
    if not torch.cuda.is_available():
        print("[INFO] CUDA is not available. Skipping LLM loading, running in Mock LLM mode (local mode).")
    else:
        print("Loading LLM (Llama-3-8B + LoRA)...")
        try:
            base_model = AutoModelForCausalLM.from_pretrained(
                "unsloth/llama-3-8b-bnb-4bit",
                device_map="auto",
                torch_dtype=torch.float16,
            )
            model     = PeftModel.from_pretrained(base_model, str(cfg.LORA_MODEL))
            tokenizer = AutoTokenizer.from_pretrained("unsloth/llama-3-8b-bnb-4bit")
            print("LLM loaded successfully.")
        except Exception as e:
            print(f"[WARN] Could not load LLM: {e}")

    # ── 3. Build SHAP background (Tuần 17 — XAI) ─────────────────────────────
    if XAI_AVAILABLE:
        try:
            csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    str(cfg.WINE_CSV))
            catalog_df_cache = pd.read_csv(csv_path).dropna(
                subset=["country","variety","description","price"]
            )
            shap_background = build_background(catalog_df_cache, n_samples=100)
            print(f"SHAP background built: {shap_background.shape}")
        except Exception as e:
            print(f"[WARN] SHAP background build failed: {e}")
    else:
        print("[INFO] XAI disabled (xai_shap module not available).")

    # ── 4. Load Semantic Catalog for TIGER + Price Rerank ───────────────────
    try:
        semantic_csv_path = str(cfg.WINE_SEMANTIC_CSV)
        print(f"Loading semantic catalog from {semantic_csv_path}...")
        catalog_df = pd.read_csv(semantic_csv_path)
        print(f"Loaded {len(catalog_df)} wines from semantic catalog.")
    except Exception as e:
        print(f"[ERROR] Could not load semantic catalog: {e}")

def generate_profile(query: str, history: List[Message] = []) -> str:
    """Uses the fine-tuned LLM to generate the ideal wine profile/Semantic ID."""
    if model is None or tokenizer is None:
        print("Warning: LLM not loaded. Using Mock Semantic ID.")
        
        # In mock mode, we use the entire conversation history to extract keywords
        full_text = " ".join([m.content for m in history]) + " " + query
        q = full_text.lower()
        if "ital" in q: return "ITAL-TUSC-SANG-2015"
        if "franc" in q: return "FRAN-BORD-REDB-2015"
        if "argentin" in q: return "ARGE-MEND-MALB-2015"
        if "port" in q: return "PORT-DOUR-PORT-2015"
        if "spain" in q or "spanish" in q: return "SPAI-RIOJ-TEMP-2015"
        return "US-CALI-CABE-2013" # Default mock semantic ID

    prompt = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nYou are a Master Sommelier. Analyze the user's request and determine the ideal structural profile of the wine. Then, output the Semantic ID of the perfect match, followed by a persuasive explanation.<|eot_id|>"
    
    for msg in history:
        prompt += f"<|start_header_id|>{msg.role}<|end_header_id|>\n{msg.content}<|eot_id|>"
        
    prompt += f"<|start_header_id|>user<|end_header_id|>\n{query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n<thought>"

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=200, stop_strings=["</thought>"], tokenizer=tokenizer)
        
    new_tokens = outputs[0][inputs.input_ids.shape[-1]:]
    generated_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
    return "<thought>" + generated_text

def generate_final_explanation(query: str, retrieved_wine: dict, history: List[Message] = []) -> str:
    """Uses RAG to generate the final sommelier explanation based on the actual retrieved wine."""
    if model is None or tokenizer is None:
        print("Warning: LLM not loaded. Using Mock Explanation.")
        return f"Based on your request for '{query}', I highly recommend the {retrieved_wine['title']}. The combination of {retrieved_wine['variety']} from {retrieved_wine['country']} offers notes of: {retrieved_wine['description']}. This is a perfect match for what you are looking for!"

    prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nYou are a Master Sommelier. Recommend the following wine based on the user's query. Explain the pairing and flavor profile persuasively.\n\nAvailable Wine: {retrieved_wine['title']}\nPrice: ${retrieved_wine['price']}\nNotes: {retrieved_wine['description']}\n<|eot_id|>"
    
    for msg in history:
        prompt += f"<|start_header_id|>{msg.role}<|end_header_id|>\n{msg.content}<|eot_id|>"
        
    prompt += f"<|start_header_id|>user<|end_header_id|>\n{query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=150)
        
    response = tokenizer.decode(outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True)
    return response

def extract_target_price(query: str) -> Optional[float]:
    """Extracts target price from the query using regex patterns."""
    query = query.lower()
    
    # 1. Look for ranges like "15-20", "$15 - $20", "15 to 20 dollars"
    range_pattern = r"\$?\s*(\d+(?:\.\d+)?)\s*(?:-|to)\s*\$?\s*(\d+(?:\.\d+)?)"
    range_match = re.search(range_pattern, query)
    if range_match:
        try:
            p1 = float(range_match.group(1))
            p2 = float(range_match.group(2))
            return (p1 + p2) / 2.0
        except ValueError:
            pass
            
    # 2. Look for single price indicators like "$45", "45$", "45 dollars", "price 45"
    price_patterns = [
        r"\$\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*(?:\$|dollars|usd)",
        r"(?:price|budget|around|under|over|about)\s*\$?\s*(\d+(?:\.\d+)?)"
    ]
    for pattern in price_patterns:
        matches = re.findall(pattern, query)
        if matches:
            try:
                return float(matches[0])
            except ValueError:
                continue
    return None

def generate_cor_response(query: str, history: List[Message] = []) -> str:
    """Uses the fine-tuned LLM to generate the entire Chain-of-Recommendation response."""
    if model is None or tokenizer is None:
        print("Warning: LLM not loaded. Using Mock CoR Response.")
        full_text = " ".join([m.content for m in history]) + " " + query
        q = full_text.lower()
        
        if "ital" in q:
            cluster_id = "11-15-06"
            rationale = "To match your preference for an Italian selection, this classic Tuscan Sangiovese is an outstanding recommendation. This wine showcases a refined profile, highlighted by dried red cherry and earthy undertones. On the palate, it offers firm tannins and bright acidity, representing excellent value."
        elif "franc" in q:
            cluster_id = "02-02-04"
            rationale = "To match your preference for a French wine, this Bordeaux red blend is an outstanding recommendation. This wine showcases a refined profile, highlighted by black currant and cedar wood. On the palate, it offers structured tannins and a long finish, representing excellent value."
        elif "argentin" in q:
            cluster_id = "12-02-06"
            rationale = "To match your preference for an Argentine wine, this Mendoza Malbec is an outstanding recommendation. This wine showcases a refined profile, highlighted by dark plum and sweet cocoa. On the palate, it offers velvety tannins and rich fruit flavors, representing excellent value."
        elif "spain" in q or "spanish" in q:
            cluster_id = "03-03-10"
            rationale = "To match your preference for a Spanish wine, this Rioja Heuristic is an outstanding recommendation. This wine showcases a refined profile, highlighted by dill and ripe red berries. On the palate, it offers integrated oak and a savory character, representing excellent value."
        else:
            cluster_id = "11-15-06"
            rationale = "To match your preference for a high-quality red wine, this Cabernet Sauvignon is an outstanding recommendation. This wine showcases a refined profile, highlighted by rich dark fruits and vanilla oak. On the palate, it offers bold structure and soft tannins, representing excellent value."
            
        return f"<thought>\nMock thought process...\n</thought>\nRationale: {rationale} -> Cluster: {cluster_id}"

    prompt = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nYou are a Master Sommelier. Analyze the user's request and determine the ideal structural profile of the wine. Then, output the Semantic ID of the perfect match, followed by a persuasive explanation.<|eot_id|>"
    
    for msg in history:
        prompt += f"<|start_header_id|>{msg.role}<|end_header_id|>\n{msg.content}<|eot_id|>"
        
    prompt += f"<|start_header_id|>user<|end_header_id|>\n{query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n<thought>"

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=350,
            pad_token_id=tokenizer.eos_token_id,
        )
        
    new_tokens = outputs[0][inputs.input_ids.shape[-1]:]
    generated_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
    return "<thought>" + generated_text

def parse_cor_response(text: str):
    """Parses Rationale and Cluster ID from the Chain-of-Recommendation response."""
    text_no_thought = text
    if "</thought>" in text:
        text_no_thought = text.split("</thought>")[-1].strip()
    
    pattern = r"Rationale:\s*(.*?)\s*->\s*Cluster:\s*(?:\[)?([0-9a-zA-Z\-_]+)(?:\])?"
    match = re.search(pattern, text_no_thought, re.DOTALL | re.IGNORECASE)
    if match:
        rationale = match.group(1).strip()
        cluster_id = match.group(2).strip()
        return rationale, cluster_id
        
    cluster_match = re.search(r"Cluster:\s*(?:\[)?([0-9a-zA-Z\-_]+)(?:\])?", text_no_thought, re.IGNORECASE)
    cluster_id = cluster_match.group(1).strip() if cluster_match else None
    
    rationale_match = re.search(r"Rationale:\s*(.*)", text_no_thought, re.IGNORECASE | re.DOTALL)
    if rationale_match:
        rationale = rationale_match.group(1).split("->")[0].strip()
    else:
        rationale = text_no_thought.split("->")[0].strip()
        
    if not cluster_id:
        xx_match = re.search(r"\b\d{2}-\d{2}-\d{2}\b", text_no_thought)
        if xx_match:
            cluster_id = xx_match.group(0)
            
    if not cluster_id:
        cluster_id = "11-15-06"
    if not rationale:
        rationale = "Here is a highly recommended selection matching your preferences."
        
    return rationale, cluster_id

def parse_query_to_json(query: str, history: List[Message] = []) -> dict:
    """Uses LLM to parse a natural query into structured JSON features."""
    if model is None or tokenizer is None:
        # Mock Parser Fallback (Heuristics based on keyword extraction)
        q = query.lower()
        
        # Extract variety
        variety_name = ""
        variety_keywords = {
            "cabernet": "Cabernet Sauvignon",
            "chardonnay": "Chardonnay",
            "pinot": "Pinot Noir",
            "sauvignon": "Sauvignon Blanc",
            "merlot": "Merlot",
            "syrah": "Syrah",
            "shiraz": "Syrah",
            "malbec": "Malbec",
            "zinfandel": "Zinfandel",
            "riesling": "Riesling",
            "tempranillo": "Tempranillo",
            "prosecco": "Glera",
            "red blend": "Red Blend",
            "white blend": "White Blend"
        }
        for k, v in variety_keywords.items():
            if k in q:
                variety_name = v
                break
                
        # Extract country
        country_name = ""
        country_keywords = {
            "us": "US", "usa": "US", "california": "US", "oregon": "US", "washington": "US",
            "france": "France", "french": "France", "italy": "Italy", "italian": "Italy",
            "spain": "Spain", "spanish": "Spain", "argentina": "Argentina", "argentinian": "Argentina",
            "chile": "Chile", "chilean": "Chile", "australia": "Australia", "australian": "Australia",
            "germany": "Germany", "german": "Germany", "portugal": "Portugal", "portuguese": "Portugal",
            "new zealand": "New Zealand", "south africa": "South Africa"
        }
        for k, v in country_keywords.items():
            if k in q:
                country_name = v
                break
                
        # Extract price
        price = extract_target_price(query)
        
        # Extract descriptors
        descriptors = []
        flavor_words = ["bold", "dry", "sweet", "light", "crisp", "smooth", "tannic", "oaky", "buttery", "fruity", "spicy", "earthy"]
        for w in flavor_words:
            if w in q:
                descriptors.append(w)
                
        return {
            "variety": variety_name,
            "country": country_name,
            "price_limit": price,
            "descriptors": descriptors
        }

    prompt = (
        "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        "You are a structured information extraction parser. Analyze the user's wine request and extract the following fields in strict JSON format: 'variety' (standard wine variety name, e.g. Pinot Noir, Cabernet Sauvignon), 'country' (standard country name, e.g. US, France, Italy, Spain), 'price_limit' (float or null), and 'descriptors' (list of flavor/style adjectives). Respond ONLY with the raw JSON block, no explanations.<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n{query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
    )
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_tokens = outputs[0][inputs.input_ids.shape[-1]:]
    generated_text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    
    try:
        json_match = re.search(r"\{.*\}", generated_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return json.loads(generated_text)
    except Exception:
        # Fallback to local parsing
        q = query.lower()
        variety_name = ""
        variety_keywords = {"cabernet": "Cabernet Sauvignon", "chardonnay": "Chardonnay", "pinot": "Pinot Noir"}
        for k, v in variety_keywords.items():
            if k in q: variety_name = v; break
        country_name = ""
        country_keywords = {"us": "US", "france": "France", "italy": "Italy"}
        for k, v in country_keywords.items():
            if k in q: country_name = v; break
        return {
            "variety": variety_name,
            "country": country_name,
            "price_limit": extract_target_price(query),
            "descriptors": []
        }

def filter_catalog_model2(parsed_json: dict) -> pd.DataFrame:
    """Applies hierarchical priority filters and re-ranking for Model 2."""
    global catalog_df
    if catalog_df is None or catalog_df.empty:
        try:
            catalog_df = pd.read_csv(str(cfg.WINE_SEMANTIC_CSV))
        except Exception:
            return pd.DataFrame()
            
    df = catalog_df.copy()
    variety = parsed_json.get("variety")
    country = parsed_json.get("country")
    price_limit = parsed_json.get("price_limit")
    descriptors = parsed_json.get("descriptors", [])
    
    # Priority 1: Variety Match
    if variety:
        variety_mask = df["variety"].str.contains(variety, case=False, na=False)
        if variety_mask.any():
            df = df[variety_mask]
            
    # Priority 2: Country Match
    if country:
        country_mask = df["country"].str.contains(country, case=False, na=False)
        if country_mask.any():
            df = df[country_mask]
            
    # Clean price
    df["_price"] = pd.to_numeric(df["price"], errors="coerce")
    
    # Priority 3: Price Proximity
    if price_limit is not None:
        df = df.dropna(subset=["_price"])
        if not df.empty:
            df["price_diff"] = (df["_price"] - price_limit).abs()
            df = df.sort_values(by=["price_diff", "points"], ascending=[True, False])
    else:
        df = df.sort_values(by="points", ascending=False)
        
    # Priority 4: Flavor Descriptors matching
    if descriptors and not df.empty:
        def calculate_flavor_score(row):
            text = str(row.get("doc_text", "")).lower()
            return sum(1 for d in descriptors if d.lower() in text)
            
        df["flavor_score"] = df.apply(calculate_flavor_score, axis=1)
        if price_limit is not None:
            max_diff = df["price_diff"].max() + 1e-9
            norm_price_sc = 1.0 - (df["price_diff"] / max_diff)
            df["combined_score"] = 0.60 * norm_price_sc + 0.40 * df["flavor_score"]
            df = df.sort_values(by="combined_score", ascending=False)
        else:
            df = df.sort_values(by="flavor_score", ascending=False)
            
    return df

def generate_sommelier_explanation_model2(query: str, retrieved_wine: dict, history: List[Message] = []) -> str:
    """Uses LLM to generate the rationale for the top wine in Model 2."""
    if model is None or tokenizer is None:
        variety = retrieved_wine.get("variety", "wine")
        country = retrieved_wine.get("country", "its origin")
        title = retrieved_wine.get("title", "this selection")
        price = retrieved_wine.get("price")
        price_str = f"${price}" if price else "N/A"
        desc = retrieved_wine.get("description", "")
        
        sentences = [s.strip() for s in re.split(r'\.(?=\s)|$', desc) if s.strip()]
        s1 = sentences[0] if len(sentences) > 0 else ""
        s2 = sentences[1] if len(sentences) > 1 else ""
        
        r1 = f"To match your preference for a {variety} from {country}, the {title} is an outstanding recommendation."
        r2 = f"This wine showcases a refined profile, highlighted by {s1.lower().rstrip('.')}."
        if s2:
            r3 = f"On the palate, it offers {s2.lower().rstrip('.')}, representing excellent value for a price of {price_str}."
        else:
            r3 = f"This is a classic expression of {variety} from the region, aligning perfectly with your budget of {price_str}."
            
        return f"{r1} {r2} {r3}"
        
    prompt = (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        f"You are a Master Sommelier. Write a highly persuasive and elegant recommendation rationale for the following wine based on the user's query.\n\n"
        f"Selected Wine: {retrieved_wine['title']}\n"
        f"Price: ${retrieved_wine['price']}\n"
        f"Notes: {retrieved_wine['description']}\n<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n{query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
    )
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_tokens = outputs[0][inputs.input_ids.shape[-1]:]
    generated_text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    return generated_text

@app.post("/recommend")
def recommend_wine(request: QueryRequest):
    try:
        import string
        clean_q = request.query.lower().translate(str.maketrans('', '', string.punctuation)).strip()
        
        greetings = ["hi", "hello", "hey", "good morning", "good evening", "chào", "xin chào"]
        thanks = ["thanks", "thank you", "cảm ơn", "cam on"]
        
        if any(g == clean_q or clean_q.startswith(g + " ") for g in greetings) and len(clean_q.split()) < 4:
            return {
                "type": "chat",
                "message": "Hello! I am your AI Sommelier. What kind of wine are you looking for today? Do you prefer red, white, or perhaps a sweet dessert wine?"
            }
            
        if any(t == clean_q or clean_q.startswith(t + " ") for t in thanks) and len(clean_q.split()) < 4:
            return {
                "type": "chat",
                "message": "You're very welcome! Let me know if you need another recommendation or have any questions about wine."
            }
            
        if len(clean_q.split()) < 3:
            return {
                "type": "chat",
                "message": "Could you provide a bit more detail? For example, are you looking for a red or white wine, and what is your price range?"
            }

        global catalog_df
        if catalog_df is None or catalog_df.empty:
            try:
                catalog_df = pd.read_csv(str(cfg.WINE_SEMANTIC_CSV))
            except Exception as e:
                print(f"[ERROR] Could not load catalog: {e}")
                catalog_df = pd.DataFrame()
                
        if catalog_df.empty:
            return {"error": "Semantic catalog is empty or not loaded."}

        # ─── MODEL 2 BRANCH ──────────────────────────────────────────────────
        if request.model_version == 2:
            print(f"[Model 2] Parsing query: {request.query}")
            parsed_json = parse_query_to_json(request.query, request.history)
            print(f"[Model 2] Parsed JSON: {parsed_json}")
            
            top_wines = filter_catalog_model2(parsed_json)
            if top_wines.empty:
                top_wines = catalog_df.head(10)
            else:
                top_wines = top_wines.head(10)
                
            top_1_row = top_wines.iloc[0]
            retrieved_metadata = {
                "title": str(top_1_row.get("title", "")),
                "price": float(top_1_row.get("price")) if pd.notna(top_1_row.get("price")) else None,
                "variety": str(top_1_row.get("variety", "")),
                "country": str(top_1_row.get("country", "")),
                "description": str(top_1_row.get("description", "")),
            }
            
            print(f"[Model 2] Generating Sommelier Explanation...")
            explanation = generate_sommelier_explanation_model2(request.query, retrieved_metadata, request.history)
            
            # Format top recommendations list
            top_recommendations_list = []
            for _, r in top_wines.iterrows():
                top_recommendations_list.append({
                    "title": str(r.get("title", "")),
                    "price": float(r.get("price")) if pd.notna(r.get("price")) else None,
                    "variety": str(r.get("variety", "")),
                    "country": str(r.get("country", "")),
                    "description": str(r.get("description", "")),
                    "Semantic_ID": str(r.get("Semantic_ID", ""))
                })
                
            # ── Phase 4: SHAP-based heuristic feature attribution ────────────
            xai_result = None
            if XAI_AVAILABLE and shap_background is not None:
                try:
                    xai_result = explain_recommendation(
                        request.query,
                        retrieved_metadata,
                        shap_background,
                        n_shap_samples=64,
                    )
                except Exception as e:
                    print(f"[WARN] SHAP explanation failed: {e}")
                    
            generated_profile_thought = f"Model 2 | Variety: {parsed_json.get('variety')} | Country: {parsed_json.get('country')}"
            
            return {
                "type"                    : "recommendation",
                "message"                 : explanation,
                "retrieved_wine"          : retrieved_metadata,
                "generated_profile_thought": generated_profile_thought,
                "xai_explanation"         : xai_result,
                "model_version"           : 2,
                "top_recommendations"     : top_recommendations_list
            }

        # ─── MODEL 1 BRANCH (DEFAULT) ────────────────────────────────────────
        print(f"[Model 1] Generating CoR response for query: {request.query}")
        cor_response = generate_cor_response(request.query, request.history)
        
        rationale, cluster_id = parse_cor_response(cor_response)
        
        matching_wines = catalog_df[catalog_df['Semantic_ID_Cluster'] == cluster_id]
        if matching_wines.empty:
            parts = cluster_id.split("-")
            if len(parts) >= 2:
                parent_cluster = f"{parts[0]}-{parts[1]}"
                matching_wines = catalog_df[catalog_df['Semantic_ID_Cluster'].str.startswith(parent_cluster, na=False)]
            if matching_wines.empty:
                matching_wines = catalog_df
                
        target_price = extract_target_price(request.query)
        matching_wines = matching_wines.copy()
        
        if target_price is not None:
            matching_wines = matching_wines.dropna(subset=['price'])
            if not matching_wines.empty:
                matching_wines['price'] = pd.to_numeric(matching_wines['price'])
                matching_wines['price_diff'] = (matching_wines['price'] - target_price).abs()
                matching_wines = matching_wines.sort_values(by=['price_diff', 'points'], ascending=[True, False])
            else:
                matching_wines = catalog_df.dropna(subset=['price']).copy()
                matching_wines['price'] = pd.to_numeric(matching_wines['price'])
                matching_wines['price_diff'] = (matching_wines['price'] - target_price).abs()
                matching_wines = matching_wines.sort_values(by=['price_diff', 'points'], ascending=[True, False])
        else:
            if 'points' in matching_wines.columns:
                matching_wines['points'] = pd.to_numeric(matching_wines['points'], errors='coerce')
                matching_wines = matching_wines.sort_values(by='points', ascending=False)
                
        top_wines = matching_wines.head(10)
        if top_wines.empty:
            top_wines = catalog_df.head(10)
            
        top_1_row = top_wines.iloc[0]
        retrieved_metadata = {
            "title": str(top_1_row.get("title", "")),
            "price": float(top_1_row.get("price")) if pd.notna(top_1_row.get("price")) else None,
            "variety": str(top_1_row.get("variety", "")),
            "country": str(top_1_row.get("country", "")),
            "description": str(top_1_row.get("description", "")),
        }
        
        # ── Phase 4: SHAP-based heuristic feature attribution ────────────
        xai_result = None
        if XAI_AVAILABLE and shap_background is not None:
            try:
                xai_result = explain_recommendation(
                    request.query,
                    retrieved_metadata,
                    shap_background,
                    n_shap_samples=64,
                )
            except Exception as e:
                print(f"[WARN] SHAP explanation failed: {e}")

                final_explanation = rationale
        if "</thought>" in final_explanation:
            final_explanation = final_explanation.split("</thought>")[-1].strip()
            
        generated_profile_thought = f"Cluster: {cluster_id}"

        return {
            "type"                    : "recommendation",
            "message"                 : final_explanation,
            "retrieved_wine"          : retrieved_metadata,
            "generated_profile_thought": generated_profile_thought,
            "xai_explanation"         : xai_result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Extra endpoints ───────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """System status — useful for demo and evaluation logging."""
    return {
        "status"         : "ok",
        "llm_loaded"     : model is not None,
        "chromadb_wines" : collection.count(),
        "xai_available"  : XAI_AVAILABLE and shap_background is not None,
        "shap_bg_shape"  : list(shap_background.shape) if shap_background is not None else None,
    }


class ExplainRequest(BaseModel):
    query : str
    title : str
    price : Optional[float] = None
    variety: str = ""
    country: str = ""
    description: str = ""


@app.post("/explain")
def explain_wine(req: ExplainRequest):
    """
    Standalone heuristic feature attribution endpoint.
    Accepts a (query, wine) pair and returns feature-level attributions.
    Useful for the demo UI and evaluation logging.
    """
    if not XAI_AVAILABLE or shap_background is None:
        raise HTTPException(status_code=503,
                            detail="XAI not available. Install shap and restart.")
    wine = {
        "title"      : req.title,
        "price"      : req.price,
        "variety"    : req.variety,
        "country"    : req.country,
        "description": req.description,
    }
    try:
        result = explain_recommendation(req.query, wine, shap_background,
                                        n_shap_samples=64)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
