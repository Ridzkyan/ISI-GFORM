import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Konfigurasi URL Google Form
FORM_URL = "https://forms.gle/XW6ErNqRwArEmXWZ7"

# Baca nama dari file list nama.txt
def read_names(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        # Menghapus baris kosong dan mengambil maksimal 100 nama
        names = [line.strip() for line in file if line.strip()]
        return names[:100]

def fill_form(name):
    # Inisialisasi WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # Wajib diaktifkan untuk deployment di server
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080') # Wajib: Atur ukuran layar virtual agar elemen tidak tertutup
    options.add_argument('--lang=id-ID') # WAJIB: Memaksa Google Form berbahasa Indonesia
    driver = webdriver.Chrome(options=options)
    
    wait = WebDriverWait(driver, 10)
    
    try:
        # Buka halaman form
        driver.get(FORM_URL)
        
        # --- HALAMAN 1 (Identitas) ---
        # 1. Isi Kolom Nama
        nama_input = wait.until(EC.presence_of_element_located((By.XPATH, '(//input[@type="text"])[1]'))) 
        nama_input.clear()
        nama_input.send_keys(name)
        
        # 2. Isi Kolom Umur (Random 20 - 22)
        random_age = str(random.randint(20, 22))
        umur_input = wait.until(EC.presence_of_element_located((By.XPATH, '(//input[@type="text"])[2]')))
        umur_input.clear()
        umur_input.send_keys(random_age)
        time.sleep(1)
        
        # 3. Klik Tombol Berikutnya (Bilingual support)
        berikutnya_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),"Berikutnya") or contains(text(),"Next")]')))
        driver.execute_script("arguments[0].click();", berikutnya_button)
        time.sleep(2)
        
        # --- HALAMAN 2 (Skala 1 - 10 Pertanyaan) ---
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="radiogroup"]')))
        radio_groups = driver.find_elements(By.XPATH, '//div[@role="radiogroup"]')
        
        # Karena di page 2, ada pertanyaan, kita isi random
        for group in radio_groups:
            if group.is_displayed():
                radios = group.find_elements(By.XPATH, './/div[@role="radio"]')
                if radios:
                    random.choice(radios).click()
                    time.sleep(0.3)
                    
        # Klik Berikutnya lagi
        berikutnya_button2 = wait.until(EC.element_to_be_clickable((By.XPATH, '(//span[contains(text(),"Berikutnya") or contains(text(),"Next")])[last()]')))
        driver.execute_script("arguments[0].click();", berikutnya_button2)
        time.sleep(2)
        
        # --- HALAMAN 3 (Skala 2 - 25 Pertanyaan) ---
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="radiogroup"]')))
        radio_groups_page3 = driver.find_elements(By.XPATH, '//div[@role="radiogroup"]')
        
        for group in radio_groups_page3:
            if group.is_displayed():
                # Untuk menghindari stale element
                try:
                    radios = group.find_elements(By.XPATH, './/div[@role="radio"]')
                    clickable_radios = [r for r in radios if r.is_displayed()]
                    if clickable_radios:
                        # Pilih random yang mana dari elemen radio untuk tidak setuju ke sangat setuju
                        random.choice(clickable_radios).click()
                        time.sleep(0.2)
                except Exception:
                    pass

        # Klik Submit (Kirim)
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),"Kirim") or contains(text(),"Submit")]')))
        driver.execute_script("arguments[0].click();", submit_button)
        time.sleep(2)
        
        print(f"Berhasil submit untuk nama: {name} | Umur: {random_age}")
        return True # Kembalikan True jika berhasil
        
    except Exception as e:
        print(f"Gagal submit untuk {name}. Error: {e}")
        return False # Kembalikan False jika gagal
    finally:
        # Tutup browser
        driver.quit()

def main():
    try:
        names = read_names('list nama.txt')
        if not names:
            print("Semua nama sudah berhasil diproses! File list nama.txt kosong.")
            return

        print(f"Sisa nama yang belum diproses: {len(names)}")
        
        # --- LOGIKA ACAK KHUSUS GITHUB ACTIONS (Dipercepat) ---
        # Karena server gratis GitHub sering "melewatkan" atau mendelay antrian cron job (tidak genap 24 kali sehari),
        # kita harus memperbesar peluang dan jumlah isian agar angka target 100/minggu tetap tercapai.
        chance = random.random()
        
        if chance < 0.15:
            to_fill = 0   # 15% Kemungkinan: Jeda TOTAL (tetap ada peluang kosong agar natural)
        elif chance < 0.50:
            to_fill = 1   # 35% Kemungkinan: Mengisi 1 form.
        elif chance < 0.85:
            to_fill = 2   # 35% Kemungkinan: Mengisi 2 form sekaligus.
        else:
            to_fill = 3   # 15% Kemungkinan: Mengisi 3 form sekaligus.

        # Pastikan tidak mau mengisi melebihi jumlah sisa nama
        to_fill = min(to_fill, len(names))

        if to_fill == 0:
            print("🕒 [JEDA ACAK] Bot memutuskan untuk TIDUR / TIDAK MENGISI pada jam ini.")
            print("Tujuannya agar terlihat seperti manusia yang kadang jeda 2-3 jam tidak mengisi sama sekali.")
            return
            
        print(f"🚀 Bot memutuskan untuk MENGISI {to_fill} DATA pada jam ini.")
        
        # Jeda AWAL acak (1 sampai 10 menit) agar tidak pernah mulai di menit yang persis sama setiap jamnya
        initial_delay = random.randint(60, 600)
        print(f"🤫 Menyamar sebagai manusia: Menunda eksekusi awal selama {initial_delay // 60} menit {initial_delay % 60} detik...")
        time.sleep(initial_delay)
        
        for i in range(to_fill):
            # Ambil data terbaru dari list
            names_current = read_names('list nama.txt')
            if not names_current: break
            
            target_name = names_current[0]
            print(f"\n[{i+1}/{to_fill}] Memproses pengisian untuk: {target_name}...")
            
            is_success = fill_form(target_name)
            
            if is_success:
                sisa_nama = names_current[1:]
                with open('list nama.txt', 'w', encoding='utf-8') as f:
                    for n in sisa_nama:
                        f.write(f"{n}\n")
                print(f"✅ Nama '{target_name}' telah dihapus dari antrian list nama.txt")
                
                # Jika ada orang selanjutnya di jam yang sama, pisahkan menitnya agak jauh agar menyebar
                if i < to_fill - 1:
                    jeda_menit = random.randint(180, 900) # 3 sampai 15 menit
                    print(f"⏳ Istirahat santai {jeda_menit // 60} menit {jeda_menit % 60} detik sebelum target berikutnya...")
                    time.sleep(jeda_menit)
            else:
                print("❌ GAGAL: Keluar dari script menggunakan exit code 1 agar GitHub Actions terbaca merah.")
                import sys
                sys.exit(1)

    except FileNotFoundError:
        print("Error: File 'list nama.txt' tidak ditemukan di folder saat ini.")

if __name__ == "__main__":
    main()
