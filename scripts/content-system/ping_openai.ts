import { pingOpenAI } from "./lib/openai.js";

async function main(): Promise<void> {
  const firstModelId = await pingOpenAI();
  console.log(`OK OpenAI reachable (${firstModelId})`);
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
