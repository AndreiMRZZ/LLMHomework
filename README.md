# Smart Librarian

Proiectul **Smart Librarian** este un chatbot AI care poate recomanda carti pe baza intereselor utilizatorului, folosind **OpenAI GPT** si **RAG (ChromaDB)**.  
Chatbotul completeaza recomandarea cu un rezumat detaliat si ofera functionalitati suplimentare precum:

- **Text to Speech (TTS)** – reda vocal raspunsurile botului direct in browser  
- **Speech to Text (STT)** – utilizatorul poate vorbi in microfon, iar vocea este transcrisa in text  

---

## Functionalitati implementate
1. **Baza de date cu rezumate (book_summaries)** – contine minim 10 carti  
2. **RAG cu ChromaDB** – cautare semantica dupa teme si contexte  
3. **Chatbot AI** – recomandari personalizate folosind GPT si vector store  
4. **Tool `get_summary_by_title(title)`** – intoarce rezumatul complet pentru o carte  
5. **Filtru de limbaj** – raspuns politicos la mesaje nepotrivite  
6. **TTS (Text to Speech)** – folosind API-ul browserului  
7. **STT (Speech to Text)** – implementat cu Whisper offline (faster-whisper)  

---

##  Tehnologii folosite
- **Backend**: Python + FastAPI  
- **Frontend**: Angular  
- **Vector Store**: ChromaDB  
- **Model AI**: OpenAI GPT (pentru raspunsuri)  
- **STT offline**: faster-whisper + ffmpeg  
- **TTS**: Web Speech API (browser)  

---

##  Cum functioneaza
- Utilizatorul poate scrie sau dicta o intrebare (STT)  
- Backend-ul cauta in vector store o carte relevanta si genereaza o recomandare cu GPT  
- Tool-ul `get_summary_by_title` adauga rezumatul complet  
- Raspunsul este afisat in chat si poate fi redat vocal (TTS)  
