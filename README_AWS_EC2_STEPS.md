# โครงงาน: The 69th National Exhibition of Art (VM1 + VM2 บน AWS EC2)

## สรุปสถาปัตยกรรม
- VM1 (DB): Ubuntu 22.04, MySQL 8, เก็บรูป **5 รูป** เป็น LONGBLOB + คำบรรยายภาษาไทย
- VM2 (Web): Ubuntu 22.04, Flask + Gunicorn + Nginx, ดึงข้อมูลรูป/คำบรรยายจาก VM1
- เครือข่าย: ใช้ VPC เดียวกัน / Subnet เดียวกัน (หรือคนละ Subnet แต่ใน VPC เดียวกัน), ให้ VM2 ต่อ MySQL ของ VM1 ผ่าน **Private IP** และเปิดอินเทอร์เน็ตเฉพาะ VM2

## ขั้นตอน (ย่อ)
1) **เตรียมรูปจริง 5 รูป** (ถ่ายจากงานจริง) นำไฟล์ไปแทนที่ `images/art1.jpg ... art5.jpg` และแก้ `descriptions.json`
2) สร้าง **VM1** (EC2 t3.micro ก็พอ) – ติดตั้ง MySQL และรัน `vm1_db_setup.sql`
3) รัน `seed.py` จากเครื่องท้องถิ่นหรือจาก VM1 เพื่อใส่ข้อมูล 5 รูป
4) สร้าง **VM2** – ติดตั้ง Python, Flask, gunicorn, nginx แล้วตั้งค่าให้เว็บออนไลน์ผ่านพอร์ต 80
5) ตั้งค่า Security Group:
   - VM1: อนุญาต TCP 22 (SSH) จาก IP ของคุณ, TCP 3306 (MySQL) จาก **Security Group ของ VM2** เท่านั้น
   - VM2: อนุญาต TCP 22 จาก IP ของคุณ, TCP 80 จาก Anywhere (0.0.0.0/0) เพื่อให้เข้าถึงผ่านอินเทอร์เน็ต
6) ทดสอบเปิดเว็บผ่าน Public IPv4 ของ VM2

## คำสั่งแบบ Step-by-Step (AWS EC2)
> ระบบปฏิบัติการแนะนำ: Ubuntu 22.04 LTS

### A. สร้าง VM1 (DB)
- เลือก AMI: Ubuntu 22.04, Instance type: t3.micro
- ผูกกับ VPC/Subnet เดียวกับ VM2 (ให้สื่อสารกันผ่าน Private IP ได้)
- สร้าง Security Group VM1: อนุญาต 22 (เฉพาะ IP คุณ) และ 3306 (จาก SG ของ VM2)
- เชื่อมต่อ SSH แล้วรัน:
```bash
sudo apt update && sudo apt install -y mysql-server python3-pip
sudo systemctl enable --now mysql

# ตั้งค่า MySQL ให้รับจากเครือข่ายภายใน:
sudo sed -i 's/^bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo systemctl restart mysql

# อัปโหลดไฟล์ vm1_db_setup.sql แล้วรัน
mysql -u root < vm1_db_setup.sql
# หรือหาก MySQL ต้องการรหัส root ให้ตั้งรหัสก่อนด้วย:
# sudo mysql_secure_installation
```

### B. ใส่ข้อมูล 5 รูป (seed)
- อัปโหลด `seed.py`, `.env`, `descriptions.json` และโฟลเดอร์ `images/` ไปไว้บน **VM1** (หรือเครื่องคุณที่เข้าถึง VM1 ได้)
- ติดตั้งไลบรารี:
```bash
pip3 install python-dotenv mysql-connector-python
```
- แก้ `.env` ให้ DB_HOST เป็น **Private IP ของ VM1** (ถ้ารันใน VM1 เองใช้ 127.0.0.1 ก็ได้)
- รัน:
```bash
python3 seed.py
```

### C. สร้าง VM2 (Web)
- เลือก AMI: Ubuntu 22.04, t3.micro
- สร้าง Security Group VM2: อนุญาต 22 (IP คุณ) และ 80 (0.0.0.0/0)
- เชื่อมต่อ SSH:
```bash
sudo apt update && sudo apt install -y python3-venv python3-pip nginx
sudo mkdir -p /opt/webapp && sudo chown $USER:$USER /opt/webapp
# อัปโหลดโฟลเดอร์ webapp/* ไปที่ /opt/webapp
cd /opt/webapp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# ทดสอบรัน:
python app.py  # เปิดพอร์ต 8000 ชั่วคราว
# กด Ctrl+C เพื่อหยุด แล้วใช้ gunicorn + nginx
deactivate
```

### D. ตั้ง Gunicorn + systemd + Nginx
```bash
sudo cp /path/to/deploy/artapp.service /etc/systemd/system/artapp.service
sudo sed -i 's|/opt/webapp|/opt/webapp|' /etc/systemd/system/artapp.service
# ตรวจสอบ WorkingDirectory ตามจริง และให้แน่ใจว่าไฟล์ app.py อยู่ที่นั่น

sudo systemctl daemon-reload
sudo systemctl enable --now artapp

# ตั้ง Nginx
sudo cp /path/to/deploy/nginx_artapp.conf /etc/nginx/sites-available/artapp
sudo ln -s /etc/nginx/sites-available/artapp /etc/nginx/sites-enabled/artapp
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
```

### E. ตั้งค่าเชื่อมต่อ DB
- เปิดไฟล์ `/opt/webapp/.env` แก้ค่า:
  - `DB_HOST=<Private IP ของ VM1>`
  - `DB_USER=artuser`
  - `DB_PASS=<รหัสที่ตั้ง>`
  - `DB_NAME=artdb`
- รีสตาร์ตบริการ:
```bash
sudo systemctl restart artapp
```

### F. ทดสอบ
- เปิดเบราว์เซอร์ไปที่ **Public IPv4 ของ VM2** (http://x.x.x.x/) จะเห็นหน้าเว็บและรูป 5 รูปพร้อมคำบรรยาย

## เคล็ดลับรายงานและสไลด์
- ใช้รูปถ่ายความละเอียดพอเหมาะ (เช่น 1600px ด้านยาว) เพื่อลดขนาด DB
- แต่ละรูปเขียนบรรยาย 1 ย่อหน้า (เหตุผลที่ชอบ, สี/องค์ประกอบ/เนื้อหา/อารมณ์, ความเชื่อมโยงส่วนตัว)
- โครงสไลด์: ปกงาน → เกริ่นงานนิทรรศการ → 5 สไลด์/5 ชิ้น → บทสรุป (สิ่งที่ได้เรียนรู้)
