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

export async function sendMessage(sessionId: string, message: string, metadata?: Record<string, any>) {
  const res = await fetch(`${API_URL}/chat/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      metadata,
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

export async function getTimeline(params?: {
  search?: string;
  days?: number;
  sort_by?: string;
  sort_order?: string;
  limit?: number;
  offset?: number;
}) {
  const searchParams = new URLSearchParams();

  if (params?.search) searchParams.set('search', params.search);
  if (params?.days) searchParams.set('days', params.days.toString());
  if (params?.sort_by) searchParams.set('sort_by', params.sort_by);
  if (params?.sort_order) searchParams.set('sort_order', params.sort_order);
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());

  const queryString = searchParams.toString();
  const url = queryString ? `${API_URL}/timeline/?${queryString}` : `${API_URL}/timeline/`;

  const res = await fetch(url, {
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

// Profile API functions
export async function getProfile() {
  const res = await fetch(`${API_URL}/auth/profile`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch profile');
  }
  return res.json();
}

export async function updateProfile(data: {
  full_name?: string;
  preferred_language?: string;
  preferred_voice?: string;
  preferences?: any;
}) {
  const res = await fetch(`${API_URL}/auth/profile`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    throw new Error('Failed to update profile');
  }
  return res.json();
}

export async function changePassword(data: {
  current_password: string;
  new_password: string;
}) {
  const res = await fetch(`${API_URL}/auth/change-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Failed to change password');
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
