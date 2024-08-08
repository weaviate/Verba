import {
  TextFieldSetting,
  NumberFieldSetting,
  SettingsPayload,
} from "./components/Settings/types";

export type ConnectPayload = {
  connected: boolean;
  error: string;
  config: { RAG: RAGConfig; SETTING: SettingsPayload };
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
  production: boolean;
  gtag: string;
  deployments: {
    WEAVIATE_URL_VERBA: string;
    WEAVIATE_API_KEY_VERBA: boolean;
  };
};

export type Status = {
  [key: string]: boolean;
};

export type SchemaStatus = {
  [key: string]: number;
};

export type ConfigResponse = {
  data: { RAG: RAGConfig; SETTING: SettingsPayload };
  error: string;
};

export type ImportResponse = {
  logging: ConsoleMessage[];
};

export type ConsoleMessage = {
  type: "INFO" | "WARNING" | "SUCCESS" | "ERROR";
  message: string;
};

export type FileData = {
  filename: string;
  extension: string;
  content: string;
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
