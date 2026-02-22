// @ts-check
const outputType = process.env.OUTPUT_TYPE ?? "";

if (!outputType) {
  throw new Error("OUTPUT_TYPE environment variable is not set.");
}

let no_header_theme = "";
let default_theme = "";

switch (outputType) {
  case "MONO":
    no_header_theme = "./theme-techbook/theme_no_header_mono.css";
    default_theme = "./theme-techbook/theme_mono.css";
    break;
  case "COLOR":
    // コードはないためひとまずカラーも同じ
    no_header_theme = "./theme-techbook/theme_no_header.css";
    default_theme = "./theme-techbook/theme_color.css";
    break;
  default:
    throw new Error(`Unknown OUTPUT_TYPE: ${outputType}`);
}

/** @type {import('@vivliostyle/cli').VivliostyleConfigSchema} */
const vivliostyleConfig = {
  title: "ホームAIエージェントスタックチャン製作記",
  author: "Atsushi Morimoto (@74th)",
  language: "ja",
  // readingProgression: 'rtl', // reading progression direction, 'ltr' or 'rtl'.
  size: "A5",
  theme: default_theme,
  image: "ghcr.io/vivliostyle/cli:8.18.0",
  entry: [
    {
      path: "./articles/0-prologue/README.md",
      theme: no_header_theme,
    },
    "./articles/1-architecture/README.md",
    {
      path: "./articles/99-epilogue/README.md",
      theme: no_header_theme,
    },

  ],
  workspaceDir: "./work",
};

module.exports = vivliostyleConfig;
