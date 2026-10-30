# Достаёт большие (256x256) иконки программ в PNG с прозрачностью — для плиток главного экрана и нижней панели.
# Источник — путь к .exe/.lnk или "shell:AppsFolder\<AppID>" (AppID смотри командой Get-StartApps).
#
# Пример:
#   .\extract_icons.ps1 -Out ps_build\exeicons -Items @{ steam = 'C:\Program Files (x86)\Steam\steam.exe'; epic = 'C:\Program Files\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe' }
#   .\extract_icons.ps1 -Out ps_build\dockicons -Items @{ chrome = 'shell:AppsFolder\Chrome'; explorer = 'shell:AppsFolder\Microsoft.Windows.Explorer' }
param(
    [Parameter(Mandatory)] [string]$Out,
    [Parameter(Mandatory)] [hashtable]$Items
)
New-Item -ItemType Directory -Force $Out | Out-Null
Add-Type -TypeDefinition @'
using System; using System.Drawing; using System.Drawing.Imaging; using System.Runtime.InteropServices;
public class MarkizIcon {
 [ComImport, Guid("bcc18b79-ba16-442f-80c4-8a59c30c463b"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
 interface IShellItemImageFactory { void GetImage(SIZE size, int flags, out IntPtr phbm); }
 [StructLayout(LayoutKind.Sequential)] struct SIZE { public int cx, cy; }
 [StructLayout(LayoutKind.Sequential)] struct BITMAP { public int bmType, bmWidth, bmHeight, bmWidthBytes; public ushort bmPlanes, bmBitsPixel; public IntPtr bmBits; }
 [DllImport("shell32.dll", CharSet=CharSet.Unicode, PreserveSig=false)] static extern void SHCreateItemFromParsingName(string path, IntPtr pbc, ref Guid riid, out IShellItemImageFactory ppv);
 [DllImport("gdi32.dll")] static extern int GetObject(IntPtr h, int c, out BITMAP b);
 [DllImport("gdi32.dll")] static extern bool DeleteObject(IntPtr h);
 public static void Save(string item, string png) {
  Guid g = new Guid("bcc18b79-ba16-442f-80c4-8a59c30c463b"); IShellItemImageFactory f; SHCreateItemFromParsingName(item, IntPtr.Zero, ref g, out f);
  IntPtr hb; SIZE s; s.cx = 256; s.cy = 256; f.GetImage(s, 0x1, out hb);
  BITMAP bm; GetObject(hb, Marshal.SizeOf(typeof(BITMAP)), out bm);
  int w = bm.bmWidth, h = bm.bmHeight, st = bm.bmWidthBytes; byte[] buf = new byte[st * h]; Marshal.Copy(bm.bmBits, buf, 0, buf.Length);
  var o = new Bitmap(w, h, PixelFormat.Format32bppArgb);
  var od = o.LockBits(new Rectangle(0, 0, w, h), ImageLockMode.WriteOnly, PixelFormat.Format32bppArgb);
  for (int y = 0; y < h; y++) Marshal.Copy(buf, (h - 1 - y) * st, IntPtr.Add(od.Scan0, y * od.Stride), w * 4);  // DIB хранится снизу вверх
  o.UnlockBits(od); o.Save(png, ImageFormat.Png); DeleteObject(hb); }
}
'@ -ReferencedAssemblies System.Drawing
foreach ($k in $Items.Keys) {
    try { [MarkizIcon]::Save($Items[$k], (Join-Path (Resolve-Path $Out) "$k.png")); Write-Host "$k — готово" }
    catch { Write-Host "$k — не получилось: $($_.Exception.Message)" }
}
