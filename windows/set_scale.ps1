# Масштаб экрана: 0 = 100 % (рекомендуемый для этого монитора), 1 = 125 %, 2 = 150 %.
# Запуск: powershell -File set_scale.ps1 1
param([int]$Step = 0)
Add-Type -TypeDefinition @'
using System; using System.Runtime.InteropServices;
public class DS {
 [StructLayout(LayoutKind.Sequential)] public struct LUID { public uint Low; public int High; }
 [StructLayout(LayoutKind.Sequential)] public struct PATH { public LUID sAd; public uint sId; public uint sMode; public uint sStat; public LUID tAd; public uint tId; public uint tMode; public uint tech; public uint rot; public uint scale; public uint rn, rd; public uint scan; public int avail; public uint tStat; public uint flags; }
 [StructLayout(LayoutKind.Sequential)] public struct MODE { public uint type, id; public LUID ad; [MarshalAs(UnmanagedType.ByValArray, SizeConst=48)] public byte[] data; }
 [StructLayout(LayoutKind.Sequential)] public struct GET { public int type; public uint size; public LUID ad; public uint id; public int min, cur, max; }
 [StructLayout(LayoutKind.Sequential)] public struct SET { public int type; public uint size; public LUID ad; public uint id; public int scaleRel; }
 [DllImport("user32.dll")] public static extern int GetDisplayConfigBufferSizes(uint f, out uint p, out uint m);
 [DllImport("user32.dll")] public static extern int QueryDisplayConfig(uint f, ref uint np, [Out] PATH[] p, ref uint nm, [Out] MODE[] m, IntPtr t);
 [DllImport("user32.dll")] public static extern int DisplayConfigGetDeviceInfo(ref GET g);
 [DllImport("user32.dll")] public static extern int DisplayConfigSetDeviceInfo(ref SET s);
 static PATH First(){ uint np, nm; GetDisplayConfigBufferSizes(2, out np, out nm); var p=new PATH[np]; var m=new MODE[nm]; QueryDisplayConfig(2, ref np, p, ref nm, m, IntPtr.Zero); return p[0]; }
 public static string Get(){ var p=First(); var g=new GET(); g.type=-3; g.size=(uint)Marshal.SizeOf(typeof(GET)); g.ad=p.sAd; g.id=p.sId; DisplayConfigGetDeviceInfo(ref g); return "cur=" + g.cur; }
 public static int Set(int rel){ var p=First(); var s=new SET(); s.type=-4; s.size=(uint)Marshal.SizeOf(typeof(SET)); s.ad=p.sAd; s.id=p.sId; s.scaleRel=rel; return DisplayConfigSetDeviceInfo(ref s); }
}
'@
[DS]::Set($Step) | Out-Null
Start-Sleep 2
[DS]::Get()
