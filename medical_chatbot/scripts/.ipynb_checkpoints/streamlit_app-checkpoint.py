import streamlit as st
st.set_page_config(page_title="Medical Chatbot", page_icon="⚕️")

import pandas as pd
import re
import os
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

# --- Load Data and Models ---

@st.cache_data # Cache data loading for performance
def load_data():
    # Path BARU: diasumsikan streamlit_app.py ada di 'scripts/'
    # dan data ada di 'data/gejala_penyakit/' RELATIF dari ROOT PROJECT,
    # jadi dari 'scripts/', kita perlu naik satu level (../)
    # lalu masuk ke 'data/gejala_penyakit/'
    df = pd.read_csv('./data/gejala_penyakit/data_penyakit.csv') 
    
    # Preprocessing (replication from notebook)
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    # Path BARU untuk stopwords_id.txt: dari 'scripts/', kita perlu naik satu level (../)
    # lalu masuk ke 'data/'
    with open(os.path.join('./data', 'stopwords_id.txt'), 'r') as f:
        stopwords_id = f.read().splitlines()

    def preprocess_text(text):
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text) # Remove non-alphanumeric
        tokens = text.split()
        stemmed_tokens = [stemmer.stem(token) for token in tokens if token not in stopwords_id]
        return " ".join(stemmed_tokens)

    df['gejala_processed'] = df['penyakit'].apply(preprocess_text)
    df['diagnosis_processed'] = df['diagnosis'].apply(preprocess_text)

    # Create unique symptom and diagnosis word lists (lookup tables)
    unique_symptoms = list(set([word for sublist in df['gejala_processed'].apply(lambda x: x.split()).tolist() for word in sublist]))
    unique_diagnosis = list(set([word for sublist in df['diagnosis_processed'].apply(lambda x: x.split()).tolist() for word in sublist]))
    
    return df, unique_symptoms, unique_diagnosis

@st.cache_resource # Cache model loading for performance
def load_bert_model():
    # Path BARU untuk model BERT: dari 'scripts/', kita perlu naik satu level (../)
    # lalu masuk ke 'models/medical_bert/model/'
    path_to_medical_bert_model = "./models/medical_bert/model/" 
    try:
        tokenizer = AutoTokenizer.from_pretrained(path_to_medical_bert_model)
        model = AutoModelForTokenClassification.from_pretrained(path_to_medical_bert_model)
        model.eval()
        return tokenizer, model
    except Exception as e:
        st.error(f"Error loading MedicalBERT model: {e}")
        st.stop() # Stop the app if model loading fails
        return None, None # Should not be reached due to st.stop()

df_penyakit, unique_symptoms, unique_diagnosis = load_data()
tokenizer, model = load_bert_model()

# --- Re-define functions from notebook (ensure they are available here) ---

def detect_medical_entities(text_input, symptom_list, diagnosis_list):
    if not isinstance(text_input, str):
        return [], []
    processed_input = text_input.lower()
    processed_input = re.sub(r'[^a-z0-9\s]', '', processed_input) # Remove non-alphanumeric
    input_tokens = processed_input.split()
    detected_symptoms = [token for token in input_tokens if token in symptom_list]
    detected_diagnoses = [token for token in input_tokens if token in diagnosis_list]
    return sorted(list(set(detected_symptoms))), sorted(list(set(detected_diagnoses)))

def bert_ner(text, tokenizer, model):
    if tokenizer is None or model is None:
        return []
    if not isinstance(text, str) or not text.strip():
        return []
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    predictions = torch.softmax(outputs.logits, dim=2).squeeze(0)
    predicted_labels = torch.argmax(predictions, dim=1)
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"].squeeze(0))
    id2label = model.config.id2label if hasattr(model.config, 'id2label') else {i: f"LABEL_{i}" for i in range(model.config.num_labels)}
    
    detected_entities = []
    
    for i, (token_id, label_id) in enumerate(zip(inputs["input_ids"].squeeze(0), predicted_labels)):
        token = tokenizer.convert_ids_to_tokens([token_id])[0]
        label = id2label.get(label_id.item(), "UNKNOWN")

        if token in tokenizer.all_special_tokens:
            continue
        
        if token.startswith("##"):
            if detected_entities and detected_entities[-1]['end_idx'] == i - 1:
                detected_entities[-1]['word'] += token[2:]
                detected_entities[-1]['end_idx'] = i
            else:
                detected_entities.append({"word": token[2:], "entity_type": label, "start_idx": i, "end_idx": i})
        else:
            detected_entities.append({"word": token, "entity_type": label, "start_idx": i, "end_idx": i})
            
    final_entities = []
    current_entity_word = ""
    current_entity_type = ""

    for item in detected_entities:
        word = item['word']
        entity_type = item['entity_type']
        
        if entity_type == 'O' or entity_type.startswith('LABEL_0') or entity_type == 'UNKNOWN':
            if current_entity_word:
                final_entities.append({'word': current_entity_word.strip(), 'entity_type': current_entity_type})
                current_entity_word = ""
                current_entity_type = ""
            continue
            
        if entity_type.startswith('B-'):
            if current_entity_word:
                final_entities.append({'word': current_entity_word.strip(), 'entity_type': current_entity_type})
            current_entity_word = word
            current_entity_type = entity_type[2:]
        elif entity_type.startswith('I-'):
            if current_entity_word and entity_type[2:] == current_entity_type:
                current_entity_word += " " + word
            else:
                if current_entity_word:
                    final_entities.append({'word': current_entity_word.strip(), 'entity_type': current_entity_type})
                current_entity_word = word
                current_entity_type = entity_type[2:]
        else:
            if current_entity_word:
                final_entities.append({'word': current_entity_word.strip(), 'entity_type': current_entity_type})
            current_entity_word = word
            current_entity_type = entity_type

    if current_entity_word:
        final_entities.append({'word': current_entity_word.strip(), 'entity_type': current_entity_type})

    return final_entities

def get_response(user_input, df, unique_symptoms, unique_diagnosis, bert_tokenizer, bert_model):
    if not user_input.strip():
        return "Halo! Ada yang bisa saya bantu terkait kesehatan Anda?"

    detected_symptoms_kw = [s for s in detect_medical_entities(user_input, unique_symptoms, unique_diagnosis)[0] if len(s) > 1]
    detected_diagnoses_kw = [d for d in detect_medical_entities(user_input, unique_symptoms, unique_diagnosis)[1] if len(d) > 1]
    
    bert_entities_raw = bert_ner(user_input, bert_tokenizer, bert_model)
    
    bert_detected_words = set()
    for entity in bert_entities_raw:
        if entity['entity_type'] == 'LABEL_1' or entity['entity_type'] == 'LABEL_2':
            if len(entity['word']) > 1:
                bert_detected_words.add(entity['word'])

    all_detected_keywords = set(detected_symptoms_kw + detected_diagnoses_kw)
    all_detected_keywords.update(bert_detected_words)

    all_detected_keywords = list(all_detected_keywords)
    
    response_parts = []

    if detected_symptoms_kw:
        response_parts.append(f"Saya mendeteksi gejala: {', '.join(detected_symptoms_kw)}.")
    
    if detected_diagnoses_kw:
        response_parts.append(f"Saya mendeteksi diagnosis: {', '.join(detected_diagnoses_kw)}.")

    if all_detected_keywords:
        relevant_rows = []
        for index, row in df.iterrows():
            gejala_text = str(row['gejala_processed'])
            diagnosis_text = str(row['diagnosis_processed'])
            
            match_count = 0
            for keyword in all_detected_keywords:
                if keyword in gejala_text.split() or keyword in diagnosis_text.split():
                    match_count += 1
            
            if match_count > 0:
                relevant_rows.append({'row': row, 'matches': match_count})
        
        relevant_rows = sorted(relevant_rows, key=lambda x: x['matches'], reverse=True)

        MIN_MATCH_THRESHOLD = 1 

        if relevant_rows and relevant_rows[0]['matches'] >= MIN_MATCH_THRESHOLD:
            top_match_row = relevant_rows[0]['row']
            diagnosis_name = str(top_match_row['diagnosis']).replace("nan", "Tidak Diketahui")
            symptoms_original = str(top_match_row['penyakit']).replace("nan", "Tidak Diketahui")

            response_parts.append(f"Berdasarkan informasi yang Anda berikan, saya menduga ini terkait dengan: **{diagnosis_name}**.")
            response_parts.append(f"Beberapa gejala terkait penyakit ini: {symptoms_original}.")
        else:
            response_parts.append("Saya tidak dapat menemukan diagnosis spesifik berdasarkan gejala yang Anda sebutkan.")
    else:
        response_parts.append("Mohon berikan detail lebih lanjut tentang gejala atau kondisi Anda.")

    final_response = " ".join(response_parts)
    return final_response if final_response else "Maaf, saya tidak memahami pertanyaan Anda. Bisakah Anda mengulanginya dengan lebih jelas?"

# --- Streamlit UI ---
st.title("⚕️ Chatbot Medis Sederhana")
st.markdown("Saya adalah chatbot medis yang dapat membantu mendeteksi gejala dan memberikan dugaan diagnosis berdasarkan informasi yang Anda berikan.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    st.markdown(f"**{message['role'].capitalize()}:** {message['content']}")

# React to user input
if prompt := st.text_input("Ketik gejala atau pertanyaan Anda di sini..."):
    # Display user message in chat message container
    st.markdown(f"**Anda:** {prompt}") # Atau st.write(f"**Anda:** {prompt}")
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get chatbot response
    with st.spinner("Mencari jawaban..."):
        response = get_response(prompt, df_penyakit, unique_symptoms, unique_diagnosis, tokenizer, model)
    
    # Display assistant response in chat message container
    st.markdown(f"**Chatbot:** {response}") # Atau st.write(f"**Chatbot:** {response}")
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("---")
st.markdown("Untuk informasi lebih lanjut, silakan konsultasi dengan tenaga medis profesional.")