#!/bin/sh
# Public-safe OpenClash settings exporter.
# Does not export subscription URLs, proxy definitions, passwords, secrets or tokens.

OUT="${1:-/tmp/openclash-settings-safe.txt}"

{
  echo "=================================================="
  echo "OpenClash Stable Configuration Snapshot"
  echo "Generated: $(date '+%Y-%m-%d %H:%M:%S %z')"
  echo "=================================================="
  echo
  echo "========== SYSTEM =========="
  echo "Kernel: $(uname -r)"
  OC_VER="$(opkg list-installed 2>/dev/null | awk '/^luci-app-openclash /{print $3; exit}')"
  echo "OpenClash: ${OC_VER:-unknown}"
  if [ -x /etc/openclash/clash ]; then
    echo -n "Mihomo: "
    /etc/openclash/clash -v 2>/dev/null | head -1
  elif [ -x /etc/openclash/core/clash_meta ]; then
    echo -n "Mihomo: "
    /etc/openclash/core/clash_meta -v 2>/dev/null | head -1
  fi

  echo
  echo "========== ALL OPENCLASH CONFIG OPTIONS =========="
  uci -q show openclash.config 2>/dev/null |
  sort |
  while IFS= read -r line; do
    key="${line%%=*}"
    key_lc="$(printf '%s' "$key" | tr 'A-Z' 'a-z')"
    case "$key_lc" in
      *password*|*passwd*|*secret*|*token*|*authentication*|*authorization*|\
      *username*|*user_name*|*dashboard_password*|*access_key*|*api_key*|\
      *private_key*|*subscribe*|*subscription*|*config_url*|*update_url*)
        printf "%s='<REDACTED>'\n" "$key"
        ;;
      *config_path*)
        printf "%s='<LOCAL_CONFIG_PATH_REDACTED>'\n" "$key"
        ;;
      *)
        printf "%s\n" "$line"
        ;;
    esac
  done

  echo
  echo "========== SECURITY NOTICE =========="
  echo "Not exported: subscription URLs, proxy/node definitions, credentials, dashboard secrets, tokens."
  echo
  echo "========== END =========="
} > "$OUT"

cat "$OUT"
