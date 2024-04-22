import { TextFieldSetting, NumberFieldSetting } from "../Settings/types";

export type RAGResponse = {
    data: RAGConfig;
    error: string;
};

export type RAGConfig = {
    [componentTitle: string]: RAGComponentClass;
};

export type RAGComponentClass = {
    selected: string;
    components: RAGComponent;
}

export type RAGComponent = {
    [key: string]: RAGComponentConfig;
}

export type RAGComponentConfig = {
    name: string
    variables: string[];
    library: string[];
    description: string[];
    selected: string;
    config: RAGSetting;
    type: string;
}

export type RAGSetting = {
    [key: string]: TextFieldSetting | NumberFieldSetting
}
