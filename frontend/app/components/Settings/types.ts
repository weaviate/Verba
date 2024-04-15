interface MetaInformation {
    title: string;
    description: string;
}

export interface SettingsConfiguration {
    Customization: CustomizationSettings
    Chat: ChatSettings
}

// Setting Options

export interface CustomizationSettings extends MetaInformation {
    settings: {
        title: TextFieldSetting;
        subtitle: TextFieldSetting;
        image: ImageFieldSetting;
    }
}

export interface ChatSettings extends MetaInformation {
    settings: {
        caching: CheckboxSetting;
        suggestion: CheckboxSetting;
    }
}

// Setting Fields

export interface TextFieldSetting {
    type: 'text';
    text: string;
    description: string;
}

export interface ImageFieldSetting {
    type: 'image';
    src: string;
    description: string;
}

export interface CheckboxSetting {
    type: 'check';
    checked: boolean;
    description: string;
}

// Base Settings

export const BaseSettings: SettingsConfiguration = {
    Customization: {
        title: "Customization",
        description: "Customize the layout of your Verba by changing the title, subtitle, logo, and colors of the app.",
        settings: {
            title: { text: "Verba", type: "text", description: "Title of the Page" },
            subtitle: { text: "The Golden RAGtriever", type: "text", description: "Subtitle of the Page" },
            image: { src: "https://github.com/weaviate/Verba/blob/main/frontend/public/favicon.png?raw=true", type: "image", description: "Logo of the Page" }
        }

    },
    Chat: {
        title: "Chat Settings",
        description: "Customize chat settings like caching generated answers in Weaviate or let Weaviate give you autocomplete suggestions.",
        settings: {
            caching: { checked: true, type: "check", description: "Should Results be cached in Weaviate?" },
            suggestion: { checked: true, type: "check", description: "Should Weaviate provide suggestions for autocompletion" }
        }

    }
}