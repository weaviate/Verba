import {
  TextFieldSetting,
  NumberFieldSetting,
  SettingsPayload,
} from "../Settings/types";

export type RAGResponse = {
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

export type RAGSetting = {
  [key: string]: TextFieldSetting | NumberFieldSetting;
};
