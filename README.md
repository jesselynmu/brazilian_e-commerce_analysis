
# Judul Project

Proyek Analisis Data: Brazilian E-Commerce Public Dataset

## Pertanyaan Bisnis

* Kota mana yang mencapai tingkat revenue penjualan tertinggi dan terendah?
* Siapa pelanggan yang menghasilkan revenue terbesar dan terkecil?
* Produk apa yang yang mempunyai penjualan terbanyak dan penjualan tersedikit?
* Produk apa yang yang mempunyai revenue penjualan tertinggi dan penjualan terendah?
* Produk apa yang mendapatkan rating tinggi dan produk apa yang mendapat rating rendah?
* Berapa banyak pesanan yang dikirim sesuai estimasi dan berapa banyak yang melewati estimasi?
* Metode pembayaran apa yang paling sering digunakan oleh pembeli, dan berapa total pendapatan yang dihasilkan?
## Setup Environment

```http
    conda create --name main-ds python=3.9
    conda activate main-ds
    pip install numpy pandas scipy matplotlib seaborn jupyter      
    streamlit babel
```

## Run Streamlit App

```http
    streamlit run dashboard.py
```