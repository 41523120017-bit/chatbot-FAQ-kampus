import re

# Kamus koreksi typo & kata singkat khas mahasiswa / kampus
TYPO_DICT = {
    "bgmn": "bagaimana",
    "cra": "cara",
    "ngisi": "isi",
    "smster": "semester",
    "smstr": "semester",
    "smt": "semester",
    "gmna": "bagaimana",
    "pmbayaran": "pembayaran",
    "byr": "bayar",
    "jdwl": "jadwal",
    "syrt": "syarat",
    "prstasi": "prestasi",
    "sy": "saya",
    "dapet": "dapat",
    "krss": "krs",
    "krsan": "krs",
    "pake": "pakai",
}

def preprocess_text(text: str) -> str:
    if not text:
        return ""
    
    # 1. Lowercasing
    text = text.lower()
    
    # 2. Cleaning: Hapus karakter khusus, simbol, dan tanda baca
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # 3. Tokenization berbasis spasi
    tokens = text.split()
    
    # 4. Typo Correction via Dictionary Mapping
    corrected_tokens = [TYPO_DICT.get(token, token) for token in tokens]
    
    # 5. Rejoin token menjadi kalimat bersih
    return " ".join(corrected_tokens)

if __name__ == "__main__":
    # Pengujian modul preprocessing
    sample = "bgmn cra ngisi krs smster 5??"
    print("Sebelum :", sample)
    print("Sesudah :", preprocess_text(sample))