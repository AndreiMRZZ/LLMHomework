import {
  Component, OnInit, ViewChild, ElementRef, inject, PLATFORM_ID
} from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
// ❗️NU mai importăm RecordRTC aici (ar accesa window la import!)

import { ApiService, RecommendResponse } from '../../service/api.service';

interface Conversation {
  title: string;
  messages: string[];
}

@Component({
  selector: 'app-smart-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './smart-chat.html',
  styleUrls: ['./smart-chat.css']
})
export class SmartChatComponent implements OnInit {
  message = '';
  history: string[] = [];
  conversations: Conversation[] = [];
  selectedIndex = -1;
  editingIndex: number | null = null;

  recorder: any;
  isRecording = false;
  loading = false;

  // ---- TTS (browser) ----
  isSpeaking = false;
  private synth: SpeechSynthesis | null = null;

  private platformId = inject(PLATFORM_ID);
  private isBrowser = isPlatformBrowser(this.platformId);

  @ViewChild('messagesBox') messagesBox!: ElementRef<HTMLDivElement>;

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadConversations();
    if (this.isBrowser) {
      this.synth = window.speechSynthesis;
    }
  }

  private scrollToBottom() {
    queueMicrotask(() => {
      if (this.messagesBox) {
        const el = this.messagesBox.nativeElement;
        el.scrollTop = el.scrollHeight;
      }
    });
  }

  // =========================
  //      CHAT BASICS
  // =========================
  sendMessage(): void {
    if (!this.message.trim()) return;
    this.startNewConversationIfNeeded();
    this.history.push(`You: ${this.message}`);
    this.message = '';
    this.updateSelectedConversation();
    this.saveConversations();
    this.scrollToBottom();
  }

  // =========================
  //      TTS (Browser)
  // =========================
  private getLastBotText(): string | null {
    for (let i = this.history.length - 1; i >= 0; i--) {
      const m = this.history[i];
      if (m.startsWith('Bot: ')) return m.replace(/^Bot:\s*/, '');
      if (m.startsWith('Summary for')) return m;
    }
    return null;
  }

  async playTTS(): Promise<void> {
    const txt = this.getLastBotText() ?? this.message.trim();
    if (!txt) return;

    if (!this.isBrowser || !this.synth) {
      console.warn('TTS indisponibil (nu e browser).');
      return;
    }

    try {
      this.synth.cancel();
      const u = new SpeechSynthesisUtterance(txt);
      u.lang = 'ro-RO';
      u.rate = 1.0;
      u.onend = () => (this.isSpeaking = false);
      u.onerror = () => (this.isSpeaking = false);

      this.isSpeaking = true;
      this.synth.speak(u);
    } catch (e) {
      console.error('Browser TTS error:', e);
      this.history.push('Bot: Eroare la TTS.');
      this.isSpeaking = false;
    } finally {
      this.updateSelectedConversation();
      this.saveConversations();
      this.scrollToBottom();
    }
  }

  stopSpeaking(): void {
    if (this.isBrowser) {
      try { this.synth?.cancel(); } finally { this.isSpeaking = false; }
    }
  }

  // =========================
  //      STT (microfon)
  // =========================
  startRecording(): void {
    if (!this.isBrowser || !navigator?.mediaDevices) {
      console.warn('STT indisponibil (nu e browser sau mediaDevices lipsă).');
      this.isRecording = false;
      return;
    }
    this.isRecording = true;
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(async stream => {
        // importăm dinamic ca să evităm accesul la window la import
        const RecordRTCDyn = (await import('recordrtc')).default;

        this.recorder = new RecordRTCDyn(stream, {
          type: 'audio',
          mimeType: 'audio/wav',
          recorderType: RecordRTCDyn.StereoAudioRecorder,
          desiredSampRate: 16000
        });
        this.recorder.startRecording();
      })
      .catch(err => {
        console.error('Microphone access denied!', err);
        this.isRecording = false;
        this.recorder = null;
      });
  }

  async stopRecording(): Promise<void> {
    if (!this.recorder || typeof this.recorder.stopRecording !== 'function') {
      this.isRecording = false;
      return;
    }

    const rec = this.recorder;
    this.recorder = null; // evită dublu-stop
    try {
      rec.stopRecording(async () => {
  const audioBlob: Blob = rec.getBlob();
  this.loading = true;
  try {
    const data = await this.api.stt(audioBlob);   // <— STTResponse tipat
    this.startNewConversationIfNeeded();
    this.message = data.transcription;
    this.history.push(`You (STT): ${data.transcription}`);
  } catch (e) {
    console.error('STT error:', e);
    this.history.push('Bot: Eroare la STT.');
  } finally {
    this.updateSelectedConversation();
    this.saveConversations();
    this.loading = false;
  }
});
    } finally {
      this.isRecording = false;
    }
  }

  // =========================
  //     RECOMMEND & SUMMARY
  // =========================
  async recommendBook(): Promise<void> {
    if (!this.message.trim()) return;
    this.startNewConversationIfNeeded();
    const userMessage = this.message;
    this.history.push(`You (recommend): ${userMessage}`);
    this.message = '';

    try {
      this.loading = true;
      const data = await this.api.recommend({ query: userMessage });
      const recommendation = (data as RecommendResponse).response;
      this.history.push(`Bot: ${recommendation}`);

      const firstLine = recommendation.split('\n')[0];
      const quoted = firstLine.match(/[„"“]([^”"]+)[”"]/) || firstLine.match(/^([^–\-:|]+)[–\-:|]/);
      const title = quoted ? quoted[1].trim() : firstLine.trim();

      await this.getSummaryByTitle(title);
    } catch (e) {
      console.error('Recommendation error:', e);
      this.history.push('Bot: Eroare la recomandare.');
    } finally {
      this.updateSelectedConversation();
      this.saveConversations();
      this.loading = false;
      this.scrollToBottom();
    }
  }

  async getSummary(): Promise<void> {
    if (!this.message.trim()) return;
    this.startNewConversationIfNeeded();
    const title = this.message.trim();
    this.history.push(`You (summary): ${title}`);
    this.message = '';
    await this.getSummaryByTitle(title);
  }

  private async getSummaryByTitle(title: string): Promise<void> {
    try {
      this.loading = true;
      const data = await this.api.summary(title);
      this.history.push(`Summary for "${data.title}": ${data.summary}`);
    } catch (e) {
      console.error('Summary error:', e);
      this.history.push('Bot: Nu am gasit rezumatul.');
    } finally {
      this.updateSelectedConversation();
      this.saveConversations();
      this.loading = false;
      this.scrollToBottom();
    }
  }

  // =========================
  //   CONVERSATIONS & STATE
  // =========================
  newChat(): void { this.saveCurrentToConversationsIfNeeded(); this.history = []; this.selectedIndex = -1; }
  selectConversation(i: number): void { this.saveCurrentToConversationsIfNeeded(); this.history = [...this.conversations[i].messages]; this.selectedIndex = i; this.editingIndex = null; }
  deleteConversation(i: number): void { this.conversations.splice(i, 1); if (this.selectedIndex === i) { this.history = []; this.selectedIndex = -1; } else if (this.selectedIndex > i) { this.selectedIndex--; } this.saveConversations(); }
  startNewConversationIfNeeded(): void { if (this.selectedIndex === -1) { const n = this.conversations.length + 1; this.conversations.push({ title: `Conversație ${n}`, messages: [] }); this.selectedIndex = this.conversations.length - 1; } }
  saveCurrentToConversationsIfNeeded(): void { if (this.history.length > 0 && this.selectedIndex === -1) { const n = this.conversations.length + 1; this.conversations.push({ title: `Conversație ${n}`, messages: [...this.history] }); } else if (this.selectedIndex >= 0) { this.conversations[this.selectedIndex].messages = [...this.history]; } this.saveConversations(); }
  updateSelectedConversation(): void { if (this.selectedIndex >= 0) { this.conversations[this.selectedIndex].messages = [...this.history]; } }
  startEditingTitle(i: number): void { this.editingIndex = i; }
  finishEditingTitle(i: number, t: string): void { if (!t.trim()) return; this.conversations[i].title = t.trim(); this.editingIndex = null; this.saveConversations(); }
  saveConversations(): void { localStorage.setItem('smartLibrarianChats', JSON.stringify(this.conversations)); }
  loadConversations(): void { const data = localStorage.getItem('smartLibrarianChats'); if (data) this.conversations = JSON.parse(data); }
}
