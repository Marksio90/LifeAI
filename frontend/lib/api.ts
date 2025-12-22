import { getAccessToken } from './auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL!;

function getAuthHeaders(): HeadersInit {
  const token = getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function startChat() {
  const res = await fetch(`${API_URL}/chat/start`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  return res.json();
}

export async function sendMessage(sessionId: string, message: string) {
  const res = await fetch(`${API_URL}/chat/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify({
      session_id: sessionId,
      message,
    }),
  });
  return res.json();
}

export async function endChat(sessionId: string) {
  const res = await fetch(`${API_URL}/chat/end`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify({
      session_id: sessionId,
    }),
  });
  return res.json();
}

export async function getTimeline() {
  const res = await fetch(`${API_URL}/timeline/`, {
    headers: getAuthHeaders(),
  });
  return res.json();
}

export async function getConversation(conversationId: string) {
  const res = await fetch(`${API_URL}/chat/conversation/${conversationId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch conversation');
  }
  return res.json();
}

export async function resumeConversation(conversationId: string) {
  const res = await fetch(`${API_URL}/chat/resume/${conversationId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to resume conversation');
  }
  return res.json();
}

// Multimodal API functions
export async function transcribeAudio(audioBlob: Blob, language?: string): Promise<any> {
  const formData = new FormData();
  formData.append('file', audioBlob, 'recording.webm');
  if (language) {
    formData.append('language', language);
  }

  const res = await fetch(`${API_URL}/multimodal/transcribe`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  });

  if (!res.ok) {
    throw new Error('Transcription failed');
  }

  return res.json();
}

export async function synthesizeSpeech(
  text: string,
  voice: string = 'nova',
  model: string = 'tts-1'
): Promise<Blob> {
  const res = await fetch(`${API_URL}/multimodal/synthesize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ text, voice, model }),
  });

  if (!res.ok) {
    throw new Error('Speech synthesis failed');
  }

  return res.blob();
}

export async function analyzeImage(
  imageFile: File,
  prompt?: string,
  analysisType: 'general' | 'food' | 'document' = 'general'
): Promise<any> {
  const formData = new FormData();
  formData.append('file', imageFile);
  if (prompt) {
    formData.append('prompt', prompt);
  }

  let endpoint = '/multimodal/vision';
  if (analysisType === 'food') {
    endpoint = '/multimodal/vision/food';
  } else if (analysisType === 'document') {
    endpoint = '/multimodal/vision/document';
  }

  const res = await fetch(`${API_URL}${endpoint}`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  });

  if (!res.ok) {
    throw new Error('Image analysis failed');
  }

  return res.json();
}
