// Node 20+ 示例：流式 + 超时 + 降级
// NK_KEY=sk-xxx node node_openai.mjs
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://nanke.pw/v1",
  apiKey: process.env.NK_KEY,
  timeout: 60_000,
  maxRetries: 1,
});

const CHAIN = ["claude-3-haiku", "deepseek-flash"];

async function chat(prompt, model) {
  const stream = await client.chat.completions.create({
    model,
    messages: [{ role: "user", content: prompt }],
    stream: true,
  });

  let text = "";
  for await (const chunk of stream) {
    const delta = chunk.choices?.[0]?.delta?.content;
    if (delta) text += delta;
  }
  if (!text) throw new Error(`empty stream from ${model}`);
  return text;
}

async function chatWithFallback(prompt) {
  let lastErr;
  for (const model of CHAIN) {
    try {
      return await chat(prompt, model);
    } catch (e) {
      lastErr = e;
      console.warn(`[warn] ${model} failed: ${e.message}`);
    }
  }
  throw lastErr;
}

console.log(await chatWithFallback("用一句话解释什么是 token 计费。"));
