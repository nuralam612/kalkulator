import math
import tkinter as tk
import tkinter.font as tkfont

AKHIR_NILAI = {"num", "const", "close", "post"}
AWAL_NILAI = {"num", "const", "func", "open"}

#Perhitungan
class Mesin:
    def __init__(self):
        self.token = []
        self.ans = 0.0
        self.baru_hitung = False

    @staticmethod
    def sin(x):
        return round(math.sin(math.radians(x)), 12)

    @staticmethod
    def cos(x):
        return round(math.cos(math.radians(x)), 12)

    @staticmethod
    def tan(x):
        if round(math.cos(math.radians(x)), 12) == 0:
            raise ValueError("tan tidak terdefinisi")
        return round(math.tan(math.radians(x)), 12)

    @staticmethod
    def fact(x):
        if x < 0 or x > 170 or x != int(x):
            raise ValueError("faktorial hanya untuk bilangan bulat 0-170")
        return float(math.factorial(int(x)))

    def tambah(self, tampil, kode, jenis):
        if self.baru_hitung:
            self.baru_hitung = False
            if jenis in ("op", "post"):
                self.token = [("Ans", f"({self.ans!r})", "const")]
            else:
                self.token = []
        if self.token and self.token[-1][2] in AKHIR_NILAI and jenis in AWAL_NILAI:
            if not (self.token[-1][2] == "num" and jenis == "num"):
                kode = "*" + kode          # perkalian otomatis, mis. 2π = 2×π
        self.token.append((tampil, kode, jenis))

    def hapus(self):
        if self.baru_hitung:
            self.bersihkan()
        elif self.token:
            self.token.pop()

    def bersihkan(self):
        self.token = []
        self.baru_hitung = False

    def teks(self):
        return "".join(t[0] for t in self.token)

    @staticmethod
    def _awal_operand(s):
        """Mencari posisi awal angka/kurung terakhir (untuk faktorial n!)."""
        i = len(s)
        if s.endswith(")"):
            dalam = 0
            while i > 0:
                i -= 1
                dalam += (s[i] == ")") - (s[i] == "(")
                if dalam == 0:
                    break
            while i > 0 and (s[i - 1].isalnum() or s[i - 1] == "_"):
                i -= 1
        else:
            while i > 0 and (s[i - 1].isalnum() or s[i - 1] in "._"):
                i -= 1
        return i

    def _persen(self, s):
        """Aturan persen seperti kalkulator pada umumnya:
        a + b%  ->  a + (a × b/100)     contoh: 800 − 50% = 400
        a × b%  ->  a × (b/100)         contoh: 200 × 15% = 30
        """
        i = self._awal_operand(s)
        if i == len(s):
            raise SyntaxError
        if i > 0 and s[i - 1] in "+-":
            j = i - 1
            k, dalam = j, 0
            while k > 0:
                c = s[k - 1]
                if c == ")":
                    dalam += 1
                elif c == "(":
                    if dalam == 0:
                        break
                    dalam -= 1
                k -= 1
            kiri = s[k:j]
            if kiri and kiri[-1] not in "+-*/(":
                return s[:i] + "((" + kiri + ")*" + s[i:] + "/100)"
        return s[:i] + "(" + s[i:] + "/100)"

    def _kode(self):
        hasil, angka = "", ""

        def simpan():
            nonlocal hasil, angka
            if angka:
                hasil += angka if "." in angka else angka + ".0"
                angka = ""

        for _, kode, jenis in self.token:
            if jenis == "num":
                if kode.startswith("*"):
                    simpan()
                    hasil += "*"
                angka += kode.lstrip("*")
            elif kode == "%":
                simpan()
                hasil = self._persen(hasil)
            elif kode == "!":
                simpan()
                i = self._awal_operand(hasil)
                if i == len(hasil):
                    raise SyntaxError
                hasil = hasil[:i] + "fact(" + hasil[i:] + ")"
            else:
                simpan()
                hasil += kode
        simpan()
        return hasil + ")" * max(0, hasil.count("(") - hasil.count(")"))

    def hitung(self):
        ekspresi = self.teks()
        ruang = {"__builtins__": {}, "sin": self.sin, "cos": self.cos, "tan": self.tan,
                 "sqrt": math.sqrt, "log": math.log10, "ln": math.log,
                 "fact": self.fact, "pi": math.pi}
        try:
            v = eval(self._kode(), ruang)
            if isinstance(v, complex) or math.isnan(v) or math.isinf(v):
                raise ValueError
            v = 0.0 if abs(v) < 1e-12 else float(v)
            self.ans = v
            self.baru_hitung = True
            return ekspresi + " =", format_angka(v), False
        except ZeroDivisionError:
            return ekspresi, "Tak bisa bagi 0", True
        except (ValueError, OverflowError, TypeError):
            return ekspresi, "Math Error", True
        except Exception:
            return ekspresi, "Syntax Error", True


def format_angka(v):
    if v == 0:
        return "0"
    s = f"{v:.10g}" if abs(v) >= 1e15 or abs(v) < 1e-9 else f"{v:.12g}"
    return s.replace(".", ",")

#Tema kalkulator
PINK_TUA = "#C2577F"
KARTU = "#FDF3F6"
LATAR_ATAS, LATAR_BAWAH = "#FDEBF1", "#F5CFDB"


def campur(a, b, f):
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * f) for x, y in zip(ca, cb))


def kotak_bulat(cv, x1, y1, x2, y2, r, **kw):
    r = max(1, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    p = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
         x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return cv.create_polygon(p, smooth=True, **kw)


def pil(cv, x1, y1, x2, y2, fill):
    d = min(x2 - x1, y2 - y1)
    r = d / 2
    kw = dict(fill=fill, outline=fill, width=1)
    cv.create_oval(x1, y1, x1 + d, y1 + d, **kw)
    cv.create_oval(x2 - d, y2 - d, x2, y2, **kw)
    if x2 - x1 >= y2 - y1:
        cv.create_rectangle(x1 + r, y1, x2 - r, y2, **kw)
    else:
        cv.create_rectangle(x1, y1 + r, x2, y2 - r, **kw)


class Tombol(tk.Canvas):
    """Tombol kapsul dengan bayangan, efek hover, dan efek tekan."""

    def __init__(self, master, teks, aksi, gaya):
        super().__init__(master, bg=KARTU, highlightthickness=0, bd=0,
                         width=50, height=40, cursor="hand2")
        self.teks, self.aksi, self.gaya = teks, aksi, gaya
        self.hover = self.tekan = False
        self.bind("<Configure>", lambda e: self.gambar())
        self.bind("<Enter>", lambda e: self._set(hover=True))
        self.bind("<Leave>", lambda e: self._set(hover=False, tekan=False))
        self.bind("<ButtonPress-1>", lambda e: self._set(tekan=True))
        self.bind("<ButtonRelease-1>", self._lepas)

    def _set(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
        self.gambar()

    def _lepas(self, e):
        tekan = self.tekan
        self._set(tekan=False)
        if tekan and 0 <= e.x <= self.winfo_width() and 0 <= e.y <= self.winfo_height():
            self.aksi()

    def gambar(self):
        self.delete("all")
        w, h, g = self.winfo_width(), self.winfo_height(), self.gaya
        bawah = h - 4
        dy = 3 if self.tekan else 0
        if not self.tekan:
            pil(self, 1, 4, w - 1, h - 1, g["bayang"])
        isi = g["isi"]
        if self.tekan:
            isi = campur(isi, PINK_TUA, 0.22)
        elif self.hover:
            isi = campur(isi, PINK_TUA, 0.08)
        pil(self, 1, 1 + dy, w - 1, bawah + dy, isi)
        self.create_text(w / 2, (1 + bawah) / 2 + dy, text=self.teks,
                         fill=g["teks"], font=g["font"])

    def kilat(self):
        self._set(tekan=True)
        self.after(110, lambda: self._set(tekan=False))


def pilih_font(daftar):
    ada = set(tkfont.families())
    return next((f for f in daftar if f in ada), "TkFixedFont")

#Tampilan kalkulator
class Aplikasi:
    def __init__(self, root):
        self.m = Mesin()
        root.title("Kalkulator Desktop")
        tinggi = min(780, root.winfo_screenheight() - 80)
        root.geometry(f"420x{tinggi}")
        root.minsize(340, 560)
        root.configure(bg=LATAR_BAWAH)

        mono = pilih_font(["JetBrains Mono", "Consolas", "Space Mono", "Ubuntu Mono",
                           "DejaVu Sans Mono", "Courier New"])
        sans = pilih_font(["Segoe UI", "Inter", "Ubuntu", "Noto Sans", "DejaVu Sans"])
        self.f_pil = tkfont.Font(family=sans, size=10, weight="bold")
        self.f_kecil = tkfont.Font(family=mono, size=11)
        self.f_ekspresi = tkfont.Font(family=mono, size=13)
        self.f_utama = tkfont.Font(family=mono, size=42)

        self.G = {
            "fungsi": {"isi": "#F8E3EA", "teks": "#6E3A52", "font": (mono, 13),
                       "bayang": "#F0D3DD"},
            "hapus": {"isi": "#F6D3D8", "teks": "#7A2E3E", "font": (sans, 15, "bold"),
                      "bayang": "#EBC1C8"},
            "op": {"isi": "#EDB8CB", "teks": "#5E2440", "font": (mono, 20),
                   "bayang": "#E0A3B9"},
            "angka": {"isi": "#FFFFFF", "teks": "#3A1F2B", "font": (mono, 20),
                      "bayang": "#EFD4DE"},
            "sama": {"isi": "#C95A84", "teks": "#FFFFFF", "font": (mono, 22, "bold"),
                     "bayang": "#B4476F"},
        }

        #Latar belakang
        self.latar = tk.Canvas(root, highlightthickness=0, bd=0, bg=LATAR_BAWAH)
        self.latar.pack(fill="both", expand=True)
        self.isi = tk.Frame(self.latar, bg=KARTU)
        self.jendela = self.latar.create_window(0, 0, window=self.isi, anchor="nw")
        self.latar.bind("<Configure>", lambda e: self.gambar_latar())
        self.isi.columnconfigure(0, weight=1)

        #Layar
        self.layar = tk.Canvas(self.isi, bg=KARTU, height=150, highlightthickness=0)
        self.layar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.layar.bind("<Configure>", lambda e: self.gambar_layar())
        self.teks_ekspresi, self.teks_utama, self.error = "", "0", False

        #Tombol
        t = self.tambah
        n = lambda d, lebar=1: (d, lambda: t(d, d, "num"), "angka", lebar)
        fungsi = [
            [("sin", lambda: t("sin(", "sin(", "func"), "fungsi", 1),
             ("cos", lambda: t("cos(", "cos(", "func"), "fungsi", 1),
             ("tan", lambda: t("tan(", "tan(", "func"), "fungsi", 1),
             ("π", lambda: t("π", "pi", "const"), "fungsi", 1)],
            [("log", lambda: t("log(", "log(", "func"), "fungsi", 1),
             ("ln", lambda: t("ln(", "ln(", "func"), "fungsi", 1),
             ("√", lambda: t("√(", "sqrt(", "func"), "fungsi", 1),
             ("x!", lambda: t("!", "!", "post"), "fungsi", 1)],
            [("(", lambda: t("(", "(", "open"), "fungsi", 1),
             (")", lambda: t(")", ")", "close"), "fungsi", 1),
             ("xʸ", lambda: t("^", "**", "op"), "fungsi", 1),
             ("%", lambda: t("%", "%", "post"), "fungsi", 1)],
        ]
        utama = [
            [("AC", self.bersihkan, "hapus", 2), ("DEL", self.hapus, "hapus", 1),
             ("÷", lambda: t("÷", "/", "op"), "op", 1)],
            [n("7"), n("8"), n("9"), ("×", lambda: t("×", "*", "op"), "op", 1)],
            [n("4"), n("5"), n("6"), ("−", lambda: t("−", "-", "op"), "op", 1)],
            [n("1"), n("2"), n("3"), ("+", lambda: t("+", "+", "op"), "op", 1)],
            [n("0", 2), (",", lambda: t(",", ".", "num"), "angka", 1),
             ("=", self.hitung, "sama", 1)],
        ]
        self.btn = {}
        self.isi.rowconfigure(1, weight=3)
        self.isi.rowconfigure(2, weight=5)
        self._susun(fungsi, baris=1, jarak=(0, 8))
        self._susun(utama, baris=2, jarak=(0, 0))

        root.bind("<Key>", self.keyboard)
        self.segarkan()

    def _susun(self, data, baris, jarak):
        panel = tk.Frame(self.isi, bg=KARTU)
        panel.grid(row=baris, column=0, sticky="nsew", pady=jarak)
        for c in range(4):
            panel.columnconfigure(c, weight=1, uniform="k")
        for r, isi_baris in enumerate(data):
            panel.rowconfigure(r, weight=1, uniform="b")
            c = 0
            for label, aksi, gaya, lebar in isi_baris:
                b = Tombol(panel, label, aksi, self.G[gaya])
                b.grid(row=r, column=c, columnspan=lebar, sticky="nsew", padx=5, pady=5)
                self.btn[label] = b
                c += lebar

    def gambar_latar(self):
        cv = self.latar
        cv.delete("gambar")
        w, h = cv.winfo_width(), cv.winfo_height()
        for y in range(0, h, 3):
            cv.create_line(0, y, w, y, width=3, tags="gambar",
                           fill=campur(LATAR_ATAS, LATAR_BAWAH, y / max(h, 1)))
        lebar = min(w - 32, 520)
        x1, y1 = (w - lebar) / 2, 14
        x2, y2 = x1 + lebar, h - 14
        for i, warna in enumerate(["#F4D2DE", "#F0C6D5", "#EBBACB"]):
            g = 6 - i * 2
            kotak_bulat(cv, x1 - g, y1 - g + 6, x2 + g, y2 + g + 6, 40,
                        fill=warna, outline="", tags="gambar")
        kotak_bulat(cv, x1, y1, x2, y2, 36, fill=KARTU, outline="#F6E1E9", tags="gambar")
        pad = 18
        cv.coords(self.jendela, x1 + pad, y1 + pad)
        cv.itemconfig(self.jendela, width=lebar - 2 * pad, height=y2 - y1 - 2 * pad)
        cv.tag_raise(self.jendela)

    def gambar_layar(self):
        cv = self.layar
        cv.delete("all")
        w, h = cv.winfo_width(), cv.winfo_height()
        pw = self.f_pil.measure("DEG") + 20
        pil(cv, 8, 14, 8 + pw, 40, PINK_TUA)
        cv.create_text(8 + pw / 2, 27, text="DEG", fill="#FFFFFF", font=self.f_pil)
        cv.create_text(w - 10, 27, text=f"Ans = {format_angka(self.m.ans)}", anchor="e",
                       fill="#8A5A6E", font=self.f_kecil)
        lebar = w - 20
        cv.create_text(w - 10, 68, text=self.potong(self.teks_ekspresi, self.f_ekspresi, lebar),
                       anchor="e", fill="#B58497", font=self.f_ekspresi)
        ukuran = 42
        self.f_utama.configure(size=ukuran)
        while self.f_utama.measure(self.teks_utama) > lebar and ukuran > 18:
            ukuran -= 2
            self.f_utama.configure(size=ukuran)
        cv.create_text(w - 10, h - 34, text=self.potong(self.teks_utama, self.f_utama, lebar),
                       anchor="e", fill=PINK_TUA if self.error else "#4A1E30",
                       font=self.f_utama)

    @staticmethod
    def potong(teks, font, lebar):
        if font.measure(teks) <= lebar:
            return teks
        while teks and font.measure("…" + teks) > lebar:
            teks = teks[1:]
        return "…" + teks

    def tampilkan(self, ekspresi, utama, error=False):
        self.teks_ekspresi, self.teks_utama, self.error = ekspresi, utama, error
        self.gambar_layar()

    def segarkan(self):
        self.tampilkan("", self.m.teks() or "0")

    def tambah(self, tampil, kode, jenis):
        self.m.tambah(tampil, kode, jenis)
        self.segarkan()

    def hapus(self):
        self.m.hapus()
        self.segarkan()

    def bersihkan(self):
        self.m.bersihkan()
        self.segarkan()

    def hitung(self):
        if self.m.token:
            self.tampilkan(*self.m.hitung())

    def keyboard(self, e):
        k, ch = e.keysym, e.char
        peta = {"+": "+", "-": "−", "*": "×", "/": "÷", "^": "xʸ", "!": "x!",
                "(": "(", ")": ")", ".": ",", ",": ",", "%": "%"}
        tombol = None
        if ch and ch.isdigit():
            tombol = self.btn[ch]
        elif ch and ch in peta:
            tombol = self.btn[peta[ch]]
        elif k in ("Return", "KP_Enter") or ch == "=":
            tombol = self.btn["="]
        elif k == "BackSpace":
            tombol = self.btn["DEL"]
        elif k == "Escape":
            tombol = self.btn["AC"]
        if tombol:
            tombol.kilat()
            tombol.aksi()


if __name__ == "__main__":
    root = tk.Tk()
    Aplikasi(root)
    root.mainloop()
