export type StatusPayload = {
    type: string
    variables: Status
    libraries: Status
    schemas: SchemaStatus
    error: string

};

export type Status = {
    [key: string]: boolean
};

export type SchemaStatus = {
    [key: string]: number
};
