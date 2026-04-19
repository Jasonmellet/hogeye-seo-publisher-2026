import fs from "node:fs/promises";
import path from "node:path";

import { getOptionalEnv, getRequiredEnv } from "./env.js";

const OPENAI_API_BASE = "https://api.openai.com/v1";
const DEFAULT_NOTES_MODEL = "gpt-5.4-mini";
const DEFAULT_NOTES_TEMPERATURE = 0.2;

function authHeaders(): HeadersInit {
  return {
    Authorization: `Bearer ${getRequiredEnv("OPENAI_API_KEY")}`
  };
}

async function expectJson(response: Response): Promise<any> {
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`OpenAI API error ${response.status}: ${body}`);
  }
  return response.json();
}

export async function pingOpenAI(): Promise<string> {
  const response = await fetch(`${OPENAI_API_BASE}/models`, {
    headers: authHeaders()
  });
  const json = await expectJson(response);
  const firstId = Array.isArray(json.data) && json.data.length > 0 ? json.data[0].id : "ok";
  return String(firstId);
}

export async function transcribeAudioFile(filePath: string): Promise<any> {
  const form = new FormData();
  const data = await fs.readFile(filePath);
  const blob = new Blob([data]);
  form.append("file", blob, path.basename(filePath));
  form.append("model", "whisper-1");
  form.append("response_format", "verbose_json");

  const response = await fetch(`${OPENAI_API_BASE}/audio/transcriptions`, {
    method: "POST",
    headers: authHeaders(),
    body: form
  });

  return expectJson(response);
}

export async function generateMarkdownFromPrompt(params: {
  system: string;
  user: string;
  model?: string;
  temperature?: number;
}): Promise<string> {
  const response = await fetch(`${OPENAI_API_BASE}/chat/completions`, {
    method: "POST",
    headers: {
      ...authHeaders(),
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: params.model || getOptionalEnv("OPENAI_NOTES_MODEL", DEFAULT_NOTES_MODEL),
      temperature: params.temperature ?? DEFAULT_NOTES_TEMPERATURE,
      messages: [
        { role: "system", content: params.system },
        { role: "user", content: params.user }
      ]
    })
  });

  const json = await expectJson(response);
  const content = json.choices?.[0]?.message?.content;
  if (typeof content !== "string" || !content.trim()) {
    throw new Error("OpenAI returned empty completion content.");
  }
  return content.trim();
}
