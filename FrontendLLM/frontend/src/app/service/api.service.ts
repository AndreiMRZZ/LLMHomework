import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../environments/environment';

export interface RecommendRequest { query: string; }
export interface RecommendResponse { response: string; }
export interface SummaryResponse { title: string; summary: string; }
export interface STTResponse      { transcription: string; }

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  recommend(body: RecommendRequest) {
    return firstValueFrom(this.http.post<RecommendResponse>(`${this.base}/recommend`, body));
  }

  summary(title: string) {
    const params = new HttpParams().set('title', title);
    return firstValueFrom(this.http.get<SummaryResponse>(`${this.base}/summary`, { params }));
  }

  async tts(query: string): Promise<Blob> {
    const res = await fetch(`${this.base}/tts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    if (!res.ok) throw new Error(`TTS failed: ${res.status}`);
    return await res.blob();
  }

stt(blob: Blob): Promise<STTResponse> {
    const fd = new FormData();
    fd.append('file', blob, 'speech.wav');
    return firstValueFrom(
      this.http.post<STTResponse>(`${this.base}/stt`, fd)
    );
  }
}
