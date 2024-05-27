export const isDevelopment =
    !process.env.NODE_ENV || process.env.NODE_ENV === "development";

export const API_URL = process.env.REACT_APP_API_URL || "https://api.color-conquerer.net";
