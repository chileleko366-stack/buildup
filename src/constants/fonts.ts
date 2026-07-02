// Font registration per 02_VISUAL_BIBLE.md (Anton + Space Grotesk).
// Self-hosted under public/fonts/ rather than fetched from Google Fonts CDN
// at render time: this session's headless Chromium doesn't trust the
// outbound TLS proxy's CA, so runtime CDN fetches fail with
// ERR_CERT_AUTHORITY_INVALID. Downloaded via curl (which does trust the
// proxy CA bundle) from the same URLs @remotion/google-fonts resolves to.
export const FONT_ANTON = "Anton";
export const FONT_SPACE_GROTESK = "Space Grotesk";
