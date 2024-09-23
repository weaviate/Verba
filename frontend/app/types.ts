export type Credentials = {
  deployment: "Weaviate" | "Docker" | "Local" | "Custom";
  url: string;
  key: string;
};

export type DocumentFilter = {
  title: string;
  uuid: string;
};

export type UserConfig = {
  getting_started: boolean;
};

export type ConnectPayload = {
  connected: boolean;
  error: string;
  rag_config: RAGConfig;
  user_config: UserConfig;
  theme: Theme;
  themes: Themes;
};

export type StatusMessage = {
  message: string;
  timestamp: string;
  type: "INFO" | "WARNING" | "SUCCESS" | "ERROR";
};

export type Suggestion = {
  query: string;
  timestamp: string;
  uuid: string;
};

export type SuggestionsPayload = {
  suggestions: Suggestion[];
};

export type AllSuggestionsPayload = {
  suggestions: Suggestion[];
  total_count: number;
};

export type StatusPayload = {
  type: string;
  variables: Status;
  libraries: Status;
  schemas: SchemaStatus;
  error: string;
};

export type HealthPayload = {
  message: string;
  production: "Local" | "Demo" | "Production";
  gtag: string;
  deployments: {
    WEAVIATE_URL_VERBA: string;
    WEAVIATE_API_KEY_VERBA: string;
  };
};

export type QueryPayload = {
  error: string;
  documents: DocumentScore[];
  context: string;
};

export type DocumentScore = {
  title: string;
  uuid: string;
  score: number;
  chunks: ChunkScore[];
};

export type ChunkScore = {
  uuid: string;
  chunk_id: number;
  score: number;
  embedder: string;
};

export type Status = {
  [key: string]: boolean;
};

export type SchemaStatus = {
  [key: string]: number;
};

export type RAGConfigResponse = {
  rag_config: RAGConfig;
  error: string;
};

export type UserConfigResponse = {
  user_config: UserConfig;
  error: string;
};

export type ThemeConfigResponse = {
  themes: Themes | null;
  theme: Theme | null;
  error: string;
};

export type DatacountResponse = {
  datacount: number;
};
export type LabelsResponse = {
  labels: string[];
};

export type ImportResponse = {
  logging: ConsoleMessage[];
};

export type ConsoleMessage = {
  type: "INFO" | "WARNING" | "SUCCESS" | "ERROR";
  message: string;
};

export type RAGConfig = {
  [componentTitle: string]: RAGComponentClass;
};

export type RAGComponentClass = {
  selected: string;
  components: RAGComponent;
};

export type RAGComponent = {
  [key: string]: RAGComponentConfig;
};

export type RAGComponentConfig = {
  name: string;
  variables: string[];
  library: string[];
  description: string[];
  selected: string;
  config: RAGSetting;
  type: string;
  available: boolean;
};

export type ConfigSetting = {
  type: string;
  value: string | number | boolean;
  description: string;
  values: string[];
};

export type RAGSetting = {
  [key: string]: ConfigSetting;
};

export type FileData = {
  fileID: string;
  filename: string;
  isURL: boolean;
  overwrite: boolean;
  extension: string;
  source: string;
  content: string;
  labels: string[];
  metadata: string;
  file_size: number;
  block?: boolean;
  status_report: StatusReportMap;
  status:
    | "READY"
    | "STARTING"
    | "LOADING"
    | "CHUNKING"
    | "EMBEDDING"
    | "INGESTING"
    | "NER"
    | "EXTRACTION"
    | "SUMMARIZING"
    | "WAITING"
    | "DONE"
    | "ERROR";
  rag_config: RAGConfig;
};

export type StatusReportMap = {
  [key: string]: StatusReport;
};

export type StatusReport = {
  fileID: string;
  status:
    | "READY"
    | "STARTING"
    | "LOADING"
    | "CHUNKING"
    | "EMBEDDING"
    | "INGESTING"
    | "NER"
    | "EXTRACTION"
    | "SUMMARIZING"
    | "DONE"
    | "WAITING"
    | "ERROR";
  message: string;
  took: number;
};

export type CreateNewDocument = {
  new_file_id: string;
  filename: string;
  original_file_id: string;
};

export const statusColorMap = {
  DONE: "bg-secondary-verba",
  ERROR: "bg-warning-verba",
  READY: "bg-button-verba",
  STARTING: "bg-button-verba",
  CHUNKING: "bg-button-verba",
  LOADING: "bg-button-verba",
  EMBEDDING: "bg-button-verba",
  INGESTING: "bg-button-verba",
  NER: "bg-button-verba",
  EXTRACTION: "bg-button-verba",
  SUMMARIZING: "bg-button-verba",
  WAITING: "bg-button-verba",
};

export const statusTextMap = {
  DONE: "Finished",
  ERROR: "Failed",
  READY: "Ready",
  STARTING: "Importing...",
  CHUNKING: "Chunking...",
  LOADING: "Loading...",
  EMBEDDING: "Embedding...",
  INGESTING: "Weaviating...",
  NER: "Extracting NER...",
  EXTRACTION: "Extraction REL...",
  SUMMARIZING: "Summarizing...",
  WAITING: "Uploading...",
};

export type FileMap = {
  [key: string]: FileData;
};

export type MetaData = {
  content: string;
  enable_ner: boolean;
  ner_labels: string[];
};

export type DocumentChunk = {
  text: string;
  doc_name: string;
  chunk_id: number;
  doc_uuid: string;
  doc_type: string;
  score: number;
};

export type DocumentPayload = {
  error: string;
  document: VerbaDocument;
};

type NodeInfo = {
  status: string;
  shards: number;
  version: string;
  name: string;
};

export type NodePayload = {
  node_count: number;
  weaviate_version: string;
  nodes: NodeInfo[];
};

// Collection payload types
type CollectionInfo = {
  name: string;
  count: number;
};

export type CollectionPayload = {
  collection_count: number;
  collections: CollectionInfo[];
};

export type MetadataPayload = {
  error: string;
  node_payload: NodePayload;
  collection_payload: CollectionPayload;
};

export type ChunksPayload = {
  error: string;
  chunks: VerbaChunk[];
};

export type ChunkPayload = {
  error: string;
  chunk: VerbaChunk;
};

export type ContentPayload = {
  error: string;
  content: ContentSnippet[];
  maxPage: number;
};

export type ContentSnippet = {
  content: string;
  chunk_id: number;
  score: number;
  type: "text" | "extract";
};

export type VectorsPayload = {
  error: string;
  vector_groups: {
    embedder: string;
    groups: VectorGroup[];
    dimensions: number;
  };
};

export type VerbaDocument = {
  title: string;
  metadata: string;
  extension: string;
  fileSize: number;
  labels: string[];
  source: string;
  meta: any;
};

export type VerbaChunk = {
  content: string;
  chunk_id: number;
  doc_uuid: string;
  pca: number[];
  umap: number[];
  start_i: number;
  end_i: number;
};

export type DocumentsPreviewPayload = {
  error: string;
  documents: DocumentPreview[];
  labels: string[];
  totalDocuments: number;
};

export type DocumentPreview = {
  title: string;
  uuid: string;
  labels: string[];
};

export type FormattedDocument = {
  beginning: string;
  substring: string;
  ending: string;
};

export type VectorGroup = {
  name: string;
  chunks: VectorChunk[];
};

export type VectorChunk = {
  vector: VerbaVector;
  chunk_id: string;
  uuid: string;
};

export type VerbaVector = {
  x: number;
  y: number;
  z: number;
};

export type DataCountPayload = {
  datacount: number;
};

export type Segment =
  | { type: "text"; content: string }
  | { type: "code"; language: string; content: string };

export interface Message {
  type: "user" | "system" | "error" | "retrieval";
  content: string | DocumentScore[];
  cached?: boolean;
  distance?: string;
  context?: string;
}

// Setting Fields

export interface TextFieldSetting {
  type: "text";
  text: string;
  description: string;
}

export interface NumberFieldSetting {
  type: "number";
  value: number;
  description: string;
}

export interface ImageFieldSetting {
  type: "image";
  src: string;
  description: string;
}

export interface CheckboxSetting {
  type: "check";
  checked: boolean;
  description: string;
}

export interface ColorSetting {
  type: "color";
  color: string;
  description: string;
}

export interface SelectSetting {
  type: "select";
  options: string[];
  value: string;
  description: string;
}

// Base Settings

const AvailableFonts: string[] = [
  "Inter",
  "Plus_Jakarta_Sans",
  "Open_Sans",
  "PT_Mono",
];

const BaseFonts: SelectSetting = {
  value: "Plus_Jakarta_Sans",
  type: "select",
  options: AvailableFonts,
  description: "Text Font",
};

export interface Theme {
  theme_name: string;
  title: TextFieldSetting;
  subtitle: TextFieldSetting;
  intro_message: TextFieldSetting;
  image: ImageFieldSetting;
  primary_color: ColorSetting;
  secondary_color: ColorSetting;
  warning_color: ColorSetting;
  bg_color: ColorSetting;
  bg_alt_color: ColorSetting;
  text_color: ColorSetting;
  text_alt_color: ColorSetting;
  button_text_color: ColorSetting;
  button_text_alt_color: ColorSetting;
  button_color: ColorSetting;
  button_hover_color: ColorSetting;
  font: SelectSetting;
  theme: "light" | "dark";
}

export const LightTheme: Theme = {
  theme_name: "Light",
  title: { text: "Verba", type: "text", description: "Title" },
  subtitle: {
    text: "The Golden RAGtriever",
    type: "text",
    description: "Subtitle",
  },
  intro_message: {
    text: "Welcome to Verba, your open-source RAG application!",
    type: "text",
    description: "First Message",
  },
  image: {
    src: "https://github.com/weaviate/Verba/blob/main/img/verba_icon.png?raw=true",
    type: "image",
    description: "Logo",
  },
  primary_color: {
    color: "#FDFF91",
    type: "color",
    description: "Primary",
  },
  secondary_color: {
    color: "#90FFA8",
    type: "color",
    description: "Secondary",
  },
  warning_color: {
    color: "#FF8399",
    type: "color",
    description: "Warning",
  },
  bg_color: {
    color: "#FEF7F7",
    type: "color",
    description: "Background",
  },
  bg_alt_color: {
    color: "#FFFFFF",
    type: "color",
    description: "Alt. Background",
  },
  text_color: { color: "#161616", type: "color", description: "Text" },
  text_alt_color: {
    color: "#8E8E8E",
    type: "color",
    description: "Alt. Text",
  },
  button_text_color: {
    color: "#161616",
    type: "color",
    description: "Button Text",
  },
  button_text_alt_color: {
    color: "#8E8E8E",
    type: "color",
    description: "Button Alt. Text",
  },
  button_color: {
    color: "#EFEFEF",
    type: "color",
    description: "Button",
  },
  button_hover_color: {
    color: "#DCDCDC",
    type: "color",
    description: "Button Hover",
  },
  font: BaseFonts,
  theme: "light",
};

export const DarkTheme: Theme = {
  ...LightTheme,
  theme_name: "Dark",
  title: { ...LightTheme.title, text: "Verba" },
  subtitle: { ...LightTheme.subtitle, text: "The Dark RAGtriever" },
  intro_message: {
    ...LightTheme.intro_message,
    text: "Welcome to Verba, your open-source RAG application!",
  },
  image: {
    ...LightTheme.image,
    src: "https://github.com/weaviate/Verba/blob/main/img/verba_icon.png?raw=true",
  },
  primary_color: { ...LightTheme.primary_color, color: "#BB86FC" },
  secondary_color: { ...LightTheme.secondary_color, color: "#008F82" },
  warning_color: { ...LightTheme.warning_color, color: "#FF8399" },
  bg_color: { ...LightTheme.bg_color, color: "#202020" },
  bg_alt_color: { ...LightTheme.bg_alt_color, color: "#2F2929" },
  text_color: { ...LightTheme.text_color, color: "#ffffff" },
  text_alt_color: { ...LightTheme.text_alt_color, color: "#999999" },
  button_text_color: { ...LightTheme.button_text_color, color: "#ffffff" },
  button_text_alt_color: {
    ...LightTheme.button_text_alt_color,
    color: "#999999",
  },
  button_color: { ...LightTheme.button_color, color: "#3C3C3C" },
  button_hover_color: { ...LightTheme.button_hover_color, color: "#2C2C2C" },
  font: { ...LightTheme.font, value: "Open_Sans" },
  theme: "dark",
};

export const WCDTheme: Theme = {
  ...LightTheme,
  theme_name: "WCD",
  title: { ...LightTheme.title, text: "Verba" },
  subtitle: { ...LightTheme.subtitle, text: "Weaviate Chatbot" },
  intro_message: {
    ...LightTheme.intro_message,
    text: "Welcome to Verba, your open-source RAG application!",
  },
  image: {
    ...LightTheme.image,
    src: "https://github.com/weaviate/Verba/blob/1.0.0/frontend/public/weaviate.png?raw=true",
  },
  primary_color: { ...LightTheme.primary_color, color: "#BF40C5" },
  secondary_color: { ...LightTheme.secondary_color, color: "#28395B" },
  warning_color: { ...LightTheme.warning_color, color: "#EA3A31" },
  bg_color: { ...LightTheme.bg_color, color: "#0C1428" },
  bg_alt_color: { ...LightTheme.bg_alt_color, color: "#192136" },
  text_color: { ...LightTheme.text_color, color: "#ffffff" },
  text_alt_color: { ...LightTheme.text_alt_color, color: "#AAAAAA" },
  button_text_color: { ...LightTheme.button_text_color, color: "#ffffff" },
  button_text_alt_color: {
    ...LightTheme.button_text_alt_color,
    color: "#AAAAAA",
  },
  button_color: { ...LightTheme.button_color, color: "#1D253A" },
  button_hover_color: { ...LightTheme.button_hover_color, color: "#313749" },
  font: { ...LightTheme.font, value: "Open_Sans" },
  theme: "dark",
};

export const WeaviateTheme: Theme = {
  ...LightTheme,
  theme_name: "Weaviate",
  title: { ...LightTheme.title, text: "Verba" },
  subtitle: { ...LightTheme.subtitle, text: "Weaviate Chatbot" },
  intro_message: {
    ...LightTheme.intro_message,
    text: "Welcome to Verba, your open-source RAG application!",
  },
  image: {
    ...LightTheme.image,
    src: "https://github.com/weaviate/Verba/blob/1.0.0/frontend/public/weaviate.png?raw=true",
  },
  primary_color: { ...LightTheme.primary_color, color: "#9bfc88" },
  secondary_color: { ...LightTheme.secondary_color, color: "#8bffe7" },
  warning_color: { ...LightTheme.warning_color, color: "#f77579" },
  bg_color: { ...LightTheme.bg_color, color: "#FEF7F7" },
  bg_alt_color: { ...LightTheme.bg_alt_color, color: "#ffffff" },
  text_color: { ...LightTheme.text_color, color: "#130C49" },
  text_alt_color: { ...LightTheme.text_alt_color, color: "#929292" },
  button_text_color: { ...LightTheme.button_text_color, color: "#130C49" },
  button_text_alt_color: {
    ...LightTheme.button_text_alt_color,
    color: "#929292",
  },
  button_color: { ...LightTheme.button_color, color: "#eeeeee" },
  button_hover_color: { ...LightTheme.button_hover_color, color: "#7dfffb" },
  font: { ...LightTheme.font, value: "Plus_Jakarta_Sans" },
  theme: "light",
};

export interface Themes {
  [key: string]: Theme;
}
