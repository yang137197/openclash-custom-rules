"""Validate the documented draft with the pinned official OpenClash Ruby helper locally."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.request

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT/'profiles/tiktok-router-loongproxy-jp-us-liangxinyun'
SOURCE_URL = 'https://raw.githubusercontent.com/vernesong/OpenClash/e553e82e01c697aefbe1555261a503f425e00ccd/luci-app-openclash/root/usr/share/openclash/YAML.rb'
SOURCE_SHA256 = '1249abf411e1df9e8fe542fb3584f34a27e6e3a587942e5d9f759a32b1bd8261'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ruby-command', default='["ruby"]', help='JSON argv for a local Ruby interpreter')
    parser.add_argument('--openclash-yaml', type=Path, help='existing official YAML.rb; hash is verified')
    parser.add_argument('--debug-log', type=Path, help='optional private historical baseline, read only and never copied')
    parser.add_argument('--report', type=Path, help='sanitized aggregate report only')
    args = parser.parse_args()
    command = json.loads(args.ruby_command)
    if not isinstance(command, list) or not command or not all(isinstance(v,str) for v in command):
        raise SystemExit('invalid Ruby argv')
    private_bytes = None
    private_input = {}
    if args.report and args.debug_log and args.report.resolve()==args.debug_log.resolve():
        raise SystemExit('report destination overlaps private input')
    if args.debug_log:
        private_bytes = args.debug_log.read_bytes()
        text = private_bytes.decode('utf-8-sig')
        blocks = re.findall(r'^## 配置文件\s*\n.*?^```yaml\s*\n(.*?)^```', text, re.M|re.S)
        if len(blocks)!=1:
            raise SystemExit('private baseline missing or ambiguous; raw details suppressed')
        try:
            # JSON transport must not silently discard a YAML alias graph in a private baseline.
            if any(isinstance(token,(yaml.tokens.AnchorToken,yaml.tokens.AliasToken)) for token in yaml.scan(blocks[0])):
                raise ValueError()
            baseline = yaml.safe_load(blocks[0])
            if not isinstance(baseline, dict):
                raise ValueError()
            private_input['privateBaseline'] = baseline
        except Exception:
            raise SystemExit('private baseline parse failed; raw details suppressed') from None
    with tempfile.TemporaryDirectory(prefix='lxy-official-merge-') as directory:
        if args.openclash_yaml:
            source_path = args.openclash_yaml.resolve(strict=True)
            data = source_path.read_bytes()
        else:
            with urllib.request.urlopen(SOURCE_URL, timeout=45) as response:
                data = response.read(1024*1024+1)
            source_path = Path(directory)/'YAML.rb'
        if hashlib.sha256(data).hexdigest()!=SOURCE_SHA256:
            raise SystemExit('official source hash mismatch')
        if not args.openclash_yaml:
            source_path.write_bytes(data)
        result = subprocess.run([*command, str(ROOT/'scripts/test_liangxinyun_incremental_merge.rb'),
                                 str(source_path), str(PROFILE/'APPLY_ROLLBACK_PLAN.md'), str(ROOT)],
                                input=json.dumps(private_input,ensure_ascii=False),
                                text=True, capture_output=True, timeout=45)
        # Never echo helper output on failure: a private baseline may be present.
        if result.returncode or result.stderr:
            raise SystemExit('official merge validation failed; raw details suppressed')
        try:
            report = json.loads(result.stdout)
            if report.get('passed') is not True:
                raise ValueError()
        except Exception:
            raise SystemExit('official merge report invalid; raw details suppressed') from None
        if args.debug_log:
            if args.debug_log.read_bytes()!=private_bytes:
                raise SystemExit('private input changed during validation')
            report['privateInputFileUnchanged'] = True
        report['sourceUrl'] = SOURCE_URL
        if args.report:
            args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        raise SystemExit('local merge verifier failed; raw details suppressed') from None
