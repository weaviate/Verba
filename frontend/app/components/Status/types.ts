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
