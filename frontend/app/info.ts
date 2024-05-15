import { Inter, Plus_Jakarta_Sans, Open_Sans, PT_Mono } from "next/font/google";

// Fonts
const inter = Inter({ subsets: ["latin"] });
const plus_jakarta_sans = Plus_Jakarta_Sans({ subsets: ["latin"] });
const open_sans = Open_Sans({ subsets: ["latin"] });
const pt_mono = PT_Mono({ subsets: ["latin"], weight: "400" });
export type FontKey = "Inter" | "Plus_Jakarta_Sans" | "Open_Sans" | "PT_Mono";

export const fonts: Record<FontKey, typeof inter> = {
  Inter: inter,
  Plus_Jakarta_Sans: plus_jakarta_sans,
  Open_Sans: open_sans,
  PT_Mono: pt_mono,
};

export const chat_interface_info =
  "Use the Chat Interface to interact with your data. Your query will be used to retrieve relevant information and to construct a response. You can choose between different Large Language Models (LLM) to create a response.";
export const chunk_interface_info =
  "Use the Chunk Interface to browse through relevant chunks of your data, based on your last query. You can choose between different embeddings and retrieval techniques.";
export const document_interface_info =
  "Use the Document Viewer to inspect your data and extracts of context that were used to generate responses to your queries. You can switch between showing the whole document and only showing the specific extract.";
