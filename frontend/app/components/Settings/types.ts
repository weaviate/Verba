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
        primary_color: ColorSetting;
        secondary_color: ColorSetting;
        warning_color: ColorSetting;
        bg_color: ColorSetting;
        bg_alt_color: ColorSetting;
        text_color: ColorSetting;
        text_alt_color: ColorSetting;
        button_color: ColorSetting;
        button_hover_color: ColorSetting;
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

export interface ColorSetting {
    type: 'color';
    color: string;
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
            image: { src: "https://github.com/weaviate/Verba/blob/main/frontend/public/favicon.png?raw=true", type: "image", description: "Logo of the Page" },
            primary_color: { color: "#FDFF91", type: "color", description: "Primary Color" },
            secondary_color: { color: "#90FFA8", type: "color", description: "Secondary Color" },
            warning_color: { color: "#FF8399", type: "color", description: "Accent Color" },
            bg_color: { color: "#FEF7F7", type: "color", description: "Background Color" },
            bg_alt_color: { color: "#FFFFFF", type: "color", description: "Alternative Background Color" },
            text_color: { color: "#161616", type: "color", description: "Text Color" },
            text_alt_color: { color: "#8E8E8E", type: "color", description: "Alternative Text Color" },
            button_color: { color: "#EFEFEF", type: "color", description: "Button Color" },
            button_hover_color: { color: "#DCDCDC", type: "color", description: "Button Hover Color" }
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