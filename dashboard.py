import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

all_df = pd.read_csv("all_df.csv")

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_total_payment_city(df):
    total_payment_city = df.groupby(by="customer_city").payment_value.sum().reset_index().sort_values(by='payment_value', ascending=False)
    return total_payment_city

def create_total_payment_customer(df):
    total_payment_customer = df.groupby(by="customer_id").payment_value.sum().reset_index().sort_values(by = 'payment_value', ascending = False)
    return total_payment_customer

def create_status_delivery(df):
    status_delivery = df.groupby(by="status_delivery").order_id.nunique().sort_values(ascending=False)
    status_delivery_df = pd.DataFrame({'status_delivery': status_delivery.index, 
                                       'count': status_delivery.values})
    return status_delivery_df

def create_product_favorite(df):
    product_favorite = df.groupby(by = "product_category_name").product_id.nunique().sort_values(ascending=False)
    product_favorite_df = pd.DataFrame({'product_category_name': product_favorite.index, 
                                        'count': product_favorite.values})
    return product_favorite_df

def create_total_payment_product(df):
    total_payment_product = df.groupby('product_category_name').payment_value.sum().reset_index().sort_values(by = 'payment_value', ascending = False)
    return total_payment_product

def create_total_rating_product(df):
    total_rating_product = df.groupby('product_category_name').review_score.mean().reset_index().sort_values(by = 'review_score', ascending = False)
    return total_rating_product

def create_total_method(df):
    total_method = df.groupby('payment_type').payment_value.agg(['count', 'sum']).reset_index().sort_values(by='sum', ascending=False)
    total_method = total_method.rename(columns={'count': 'total_usage', 
                                                'sum': 'total_payment'})
    return total_method

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": "max",
    "order_id": "nunique",
    "payment_value": "sum"
})
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

datetime_columns = ["order_purchase_timestamp", "order_approved_at", 
                    "order_delivered_carrier_date", "order_delivered_customer_date",
                    "order_estimated_delivery_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    st.image('logo.png')

    st.header('Gunakan Filter Dibawah Ini')

    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
total_payment_city = create_total_payment_city(main_df)
total_payment_customer = create_total_payment_customer(main_df)
status_delivery_df = create_status_delivery(main_df)
product_favorite_df = create_product_favorite(main_df)
total_payment_product = create_total_payment_product(main_df)
total_rating_product = create_total_rating_product(main_df)
total_method = create_total_method(main_df)
rfm_df = create_rfm_df(main_df)

st.header('Proyek Analisis Data: Brazilian E-Commerce Public Dataset')

st.subheader('Penjualan Harian')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#FC6736"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader("5 Kota Tertinggi dan Terendah Berdasarkan Revenue")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#FC6736", "#FFDD95", "#FFDD95", "#FFDD95", "#FFDD95"]

sns.barplot(x="payment_value", y="customer_city", data=total_payment_city.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Kota Dengan Tingkat Revenue Tertinggi", loc="center", fontsize=18)
ax[0].tick_params(axis ='y', labelsize=15)

sns.barplot(x="payment_value", y="customer_city", data=total_payment_city.sort_values(by="payment_value", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Kota Dengan Tingkat Revenue Terendah", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=15)
 
st.pyplot(fig)

st.subheader("5 Customer Dengan Revenue Terbesar dan Terkecil")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#FC6736", "#FFDD95", "#FFDD95", "#FFDD95", "#FFDD95"]

sns.barplot(x="payment_value", y="customer_id", data=total_payment_customer.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Customer Dengan Revenue Terbesar", loc="center", fontsize=18)
ax[0].tick_params(axis ='y', labelsize=15)

sns.barplot(x="payment_value", y="customer_id", data=total_payment_customer.sort_values(by="payment_value", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Customer Dengan Reveneu Terkecil", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=15)

st.pyplot(fig)

st.subheader("5 Produk Dengan Penjualan Terbanyak dan Tersedikit")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#FC6736", "#FFDD95", "#FFDD95", "#FFDD95", "#FFDD95"]

sns.barplot(x="count", y="product_category_name", data=product_favorite_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Produk Dengan Penjualan Terbanyak", loc="center", fontsize=18)
ax[0].tick_params(axis ='y', labelsize=15)

sns.barplot(x="count", y="product_category_name", data=product_favorite_df.sort_values(by="count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk Dengan Penjualan Tersedikit", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=15)

st.pyplot(fig)

st.subheader("5 Produk Dengan Revenue Penjualan Tertinggi dan Terendah")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#FC6736", "#FFDD95", "#FFDD95", "#FFDD95", "#FFDD95"]

sns.barplot(x="payment_value", y="product_category_name", data=total_payment_product.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Produk Dengan Revenue Terbesar", loc="center", fontsize=18)
ax[0].tick_params(axis ='y', labelsize=15)

sns.barplot(x="payment_value", y="product_category_name", data=total_payment_product.sort_values(by="payment_value", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Product Dengan Revenue Terkecil", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=15)

st.pyplot(fig)

st.subheader("5 Produk Dengan Rating Tertinggi dan Terendah")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#FC6736", "#FFDD95", "#FFDD95", "#FFDD95", "#FFDD95"]

sns.barplot(x="review_score", y="product_category_name", data=total_rating_product.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Produk Dengan Rating Tertinggi", loc="center", fontsize=18)
ax[0].tick_params(axis ='y', labelsize=15)

sns.barplot(x="review_score", y="product_category_name", data=total_rating_product.sort_values(by="review_score", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk Dengan Rating Terendah", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=15)

st.pyplot(fig)

st.subheader("Persentase Pesanan yang Dikirim Sesuai Estimasi")

fig, ax = plt.subplots(figsize=(4, 4))
colors = ["#FC6736", "#FFDD95"]
ax.pie(status_delivery_df['count'], labels=status_delivery_df['status_delivery'], autopct='%1.1f%%', colors=colors, startangle=90)

st.pyplot(fig)

st.subheader("Metode Pembayang yang Digunakan")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))

colors = ["#FC6736", "#FFDD95", "#FFDD95", "#FFDD95"]

sns.barplot(y="total_usage", x="payment_type", data=total_method.sort_values(by="total_usage", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Berdasarkan Jumlah", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15)

sns.barplot(y="total_payment", x="payment_type", data=total_method.sort_values(by="total_payment", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("Berdasarkan Hasil Pendapatan", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Pelanggan Terbaik Berdasarkan Parameter RFM")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#FC6736", "#FC6736", "#FC6736", "#FC6736", "#FC6736"]
 
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45, ha='right')
 
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45, ha='right')
 
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=45, ha='right')
 
st.pyplot(fig)
 
st.markdown("<p style='text-align:center;'>Jesselyn Mu - February 2024</p>", unsafe_allow_html=True)