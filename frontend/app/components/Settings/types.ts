interface SettingGroup<T> {
    title: string;
    description: string;
    settings: T;
}

export interface SettingsConfiguration {
    [key: string]: SettingGroup<any>;
}

export interface CustomizationSettings {
    title: TextFieldSetting;
    subtitle: TextFieldSetting;
    image: ImageFieldSetting;
}

export interface ChatSettings {
    caching: CheckboxSetting;
    suggestion: CheckboxSetting;
}

export interface TextFieldSetting {
    text: string;
}

export interface ImageFieldSetting {
    encoding: string;
}

export interface CheckboxSetting {
    checked: boolean;
    description?: string;
}


export const BaseSettings: SettingsConfiguration = {
    Customization: {
        title: "Customization",
        description: "Customize the layout of your Verba by changing the title, subtitle, logo, and colors of the app.",
        settings: {
            title: { text: "Verba" },
            subtitle: { text: "The Golden RAGtriever" },
            image: { encoding: "https://github.com/weaviate/Verba/blob/main/frontend/public/favicon.png?raw=true" }
        }

    },
    Chat: {
        title: "Chat Settings",
        description: "Customize chat settings like caching generated answers in Weaviate or let Weaviate give you autocomplete suggestions.",
        settings: {
            caching: { checked: true },
            suggestion: { checked: true }
        }

    }
}