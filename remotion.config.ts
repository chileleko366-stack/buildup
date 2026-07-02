/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { existsSync } from "node:fs";
import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// Dev-container-specific workaround (see CLAUDE.md "Environment quirk"):
// this session's egress policy blocks Remotion's own headless-shell
// download from remotion.media, so a pre-installed Playwright browser is
// used instead. That exact path only exists in THIS container image --
// on a real CI runner (e.g. GitHub Actions' ubuntu-latest) it won't exist,
// and Remotion should fall back to its normal behavior (download its own
// headless shell, which is not blocked on a real runner's unrestricted
// egress). Gated on existsSync so this is a no-op anywhere else, rather
// than a hardcoded path that would break CI silently or loudly.
const DEV_CONTAINER_BROWSER_PATH =
  "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell";
if (existsSync(DEV_CONTAINER_BROWSER_PATH)) {
  Config.setBrowserExecutable(DEV_CONTAINER_BROWSER_PATH);
}
