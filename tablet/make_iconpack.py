# Пакет иконок MARKIZ NIGHT для Nova / Smart Launcher и других лаунчеров с поддержкой ADW-паков.
# Берёт иконки из theme_build/icons (их рисует make_theme.py), собирает APK через aapt2
# и подписывает схемой v1 (JAR) на Python, потому что рабочей Java на компе нет.
# Запуск: python make_iconpack.py          — неоновые иконки (theme_build/icons)
#         python make_iconpack.py ps_build — плитки в стиле консоли (ps_build/icons, рисует make_ps.py)
import base64, hashlib, io, os, re, shutil, subprocess, sys, zipfile, datetime
from PIL import Image
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs7
from cryptography.x509.oid import NameOID

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(os.path.expanduser("~"), "android-build")
BT = os.path.join(TOOLS, "bt", "android-14")
AAPT2, ZIPALIGN, ANDROID_JAR = os.path.join(BT, "aapt2.exe"), os.path.join(BT, "zipalign.exe"), os.path.join(TOOLS, "android.jar")
ICONS = os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else "theme_build", "icons")
VERSION = 3 # поднимать при каждой пересборке, иначе поверх установленного пака не встанет
OUT = os.path.join(HERE, "iconpack_build")
KEY = os.path.join(HERE, "iconpack_key.pem")  # свой ключ: обновления пака подписываются им же
PKG = "land.markiz.night.icons"

def dname(pkg):
    return "ic_" + re.sub(r"[^a-z0-9_]", "_", pkg.lower())

def main():
    shutil.rmtree(OUT, ignore_errors=True)
    res = os.path.join(OUT, "res")
    os.makedirs(os.path.join(res, "drawable-nodpi")); os.makedirs(os.path.join(res, "xml")); os.makedirs(os.path.join(res, "values"))
    comps = [l.strip() for l in open(os.path.join(HERE, "components.txt"), encoding="ascii") if "/" in l]
    have = {f[:-4] for f in os.listdir(ICONS) if f.endswith(".png") and f.startswith(("com.", "org.", "ru.", "cn.", "app."))}
    items, draws = [], set()
    for c in comps:
        pkg, act = c.split("/", 1)
        if act.startswith("."): act = pkg + act
        if pkg in have:
            items.append((f"{pkg}/{act}", dname(pkg))); draws.add(pkg)
    for pkg in draws:
        shutil.copy(os.path.join(ICONS, pkg + ".png"), os.path.join(res, "drawable-nodpi", dname(pkg) + ".png"))
    # Подложка (iconback) и маска (iconmask) для остальных приложений
    # Берём готовую иконку (рамка розовая) и затираем глиф в центре цветом плашки:
    # поверх ляжет уменьшенная родная иконка приложения
    back = Image.open(os.path.join(ICONS, "app.netlify.funny_syrniki_05be44.twa.png")).convert("RGBA"); px = back.load()
    for y in range(40, 152):
        for x in range(40, 152):
            px[x, y] = back.getpixel((28, y))
    back.save(os.path.join(res, "drawable-nodpi", "iconback.png"))
    mask = Image.new("RGBA", (192, 192), (0, 0, 0, 0))
    from PIL import ImageDraw
    ImageDraw.Draw(mask).rounded_rectangle((10, 10, 182, 182), radius=46, fill=(0, 0, 0, 255))
    mask.save(os.path.join(res, "drawable-nodpi", "iconmask.png"))
    appfilter = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>",
                 '  <iconback img1="iconback" />', '  <iconmask img1="iconmask" />', '  <scale factor="0.62" />']
    appfilter += [f'  <item component="ComponentInfo{{{c}}}" drawable="{d}" />' for c, d in items]
    appfilter.append("</resources>")
    xml = "\n".join(appfilter) + "\n"
    open(os.path.join(res, "xml", "appfilter.xml"), "w", encoding="utf-8").write(xml)
    drawable = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>", '  <version>1</version>', '  <category title="MARKIZ NIGHT" />']
    drawable += [f'  <item drawable="{dname(p)}" />' for p in sorted(draws)]
    drawable.append("</resources>")
    open(os.path.join(res, "xml", "drawable.xml"), "w", encoding="utf-8").write("\n".join(drawable) + "\n")
    open(os.path.join(res, "values", "strings.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources><string name="app_name">MARKIZ NIGHT icons</string></resources>\n')
    filters = "".join(f'<intent-filter><action android:name="{a}"/><category android:name="android.intent.category.DEFAULT"/></intent-filter>'
                      for a in ("org.adw.launcher.THEMES", "com.novalauncher.THEME", "com.gau.go.launcherex.theme", "com.teslacoilsw.launcher.THEME",
                                "ginlemon.smartlauncher.THEMES", "com.fede.launcher.THEME_ICONPACK", "com.anddoes.launcher.THEME"))
    icon = dname("app.netlify.funny_syrniki_05be44.twa")
    open(os.path.join(OUT, "AndroidManifest.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="utf-8"?>\n<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="{PKG}" '
        f'android:versionCode="{VERSION}" android:versionName="1.{VERSION - 1}">\n<uses-sdk android:minSdkVersion="21" android:targetSdkVersion="28"/>\n'
        f'<application android:label="@string/app_name" android:icon="@drawable/{icon}" android:hasCode="false">\n'
        f'<activity android:name="android.app.Activity" android:exported="true">{filters}</activity>\n</application>\n</manifest>\n')
    # Сборка: aapt2 compile + link
    flat = os.path.join(OUT, "flat.zip")
    subprocess.run([AAPT2, "compile", "--dir", res, "-o", flat], check=True)
    unsigned = os.path.join(OUT, "unsigned.apk")
    subprocess.run([AAPT2, "link", "-o", unsigned, "-I", ANDROID_JAR, "--manifest", os.path.join(OUT, "AndroidManifest.xml"), flat], check=True)
    # Некоторые лаунчеры читают appfilter из assets
    with zipfile.ZipFile(unsigned, "a", zipfile.ZIP_DEFLATED) as z:
        z.writestr("assets/appfilter.xml", xml)
    signed = os.path.join(OUT, "signed.apk"); sign_v1(unsigned, signed)
    final = os.path.join(HERE, "MARKIZ_NIGHT_icons.apk")
    subprocess.run([ZIPALIGN, "-f", "-p", "4", signed, final], check=True)
    print(final, len(items), "components", len(draws), "icons")

def key_and_cert():
    if os.path.exists(KEY):
        data = open(KEY, "rb").read()
        key = serialization.load_pem_private_key(data, None)
        cert = x509.load_pem_x509_certificate(data[data.index(b"-----BEGIN CERTIFICATE"):])
        return key, cert
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "MARKIZ LAND")])
    now = datetime.datetime(2026, 1, 1)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(now).not_valid_after(now + datetime.timedelta(days=365 * 30))
            .sign(key, hashes.SHA256()))
    open(KEY, "wb").write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
                          + cert.public_bytes(serialization.Encoding.PEM))
    return key, cert

def sign_v1(src, dst):
    key, cert = key_and_cert()
    b64 = lambda b: base64.b64encode(b).decode()
    zin = zipfile.ZipFile(src)
    names = [i.filename for i in zin.infolist() if not i.filename.startswith("META-INF/")]
    mf = "Manifest-Version: 1.0\r\nCreated-By: MARKIZ LAND\r\n\r\n"
    sf_entries = ""
    for n in names:
        sec = f"Name: {n}\r\nSHA-256-Digest: {b64(hashlib.sha256(zin.read(n)).digest())}\r\n\r\n"
        mf += sec
        sf_entries += f"Name: {n}\r\nSHA-256-Digest: {b64(hashlib.sha256(sec.encode()).digest())}\r\n\r\n"
    sf = (f"Signature-Version: 1.0\r\nSHA-256-Digest-Manifest: {b64(hashlib.sha256(mf.encode()).digest())}\r\n"
          f"Created-By: MARKIZ LAND\r\n\r\n") + sf_entries
    sig = (pkcs7.PKCS7SignatureBuilder().set_data(sf.encode()).add_signer(cert, key, hashes.SHA256())
           .sign(serialization.Encoding.DER, [pkcs7.PKCS7Options.DetachedSignature, pkcs7.PKCS7Options.NoAttributes, pkcs7.PKCS7Options.Binary]))
    with zipfile.ZipFile(dst, "w") as zout:
        zout.writestr("META-INF/MANIFEST.MF", mf); zout.writestr("META-INF/CERT.SF", sf); zout.writestr("META-INF/CERT.RSA", sig)
        for i in zin.infolist():
            if not i.filename.startswith("META-INF/"):
                zout.writestr(i, zin.read(i.filename))

main()
