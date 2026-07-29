# ==================================================
# تطبيق المحلل الفني المتكامل - قائمة الأصول والقفل
# ==================================================

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands
import plotly.graph_objects as go
import pywhatkit as kit
from datetime import datetime

# --------------------------
# إعدادات الواجهة الأساسية
# --------------------------
st.set_page_config(
    page_title="محلل التداول الذكي - نظام الاشتراكات",
    layout="wide",
    page_icon="📊"
)

css_اخفاء = """
<style>
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding: 1rem 2rem;}
</style>
"""
st.markdown(css_اخفاء, unsafe_allow_html=True)

# --------------------------
# قاعدة بيانات الاشتراكات
# --------------------------
المشتركين_المعتمدين = {
    "ZAZA-2026-VIP1": "2026-12-31",
    "TRADER-MONTH-99": "2026-08-30",
    "EXPERT-FREE-TEST": "2026-07-30"
}

st.sidebar.header("🔐 نظام الاشتراكات الشهرية")
رمز_الاشتراك = st.sidebar.text_input("أدخل مفتاح الاشتراك الشهري:", type="password")

def التحقق_من_الاشتراك(مفتاح):
    if not مفتاح:
        return False, "الرجاء إدخال مفتاح الاشتراك."
    if مفتاح in المشتركين_المعتمدين:
        تاريخ_الانتهاء = datetime.strptime(المشتركين_المعتمدين[مفتاح], "%Y-%m-%d")
        if datetime.now() <= تاريخ_الانتهاء:
            return True, f"الاشتراك ساري حتى: {المشتركين_المعتمدين[مفتاح]}"
        else:
            return False, "انتهت صلاحية هذا المفتاح الشهري."
    return False, "مفتاح الاشتراك غير صحيح."

حالة_الاشتراك, رسالة_الاشتراك = التحقق_من_الاشتراك(رمز_الاشتراك)

# --------------------------
# صفحة الدفع والاشتراك (إذا لم يكن مفعلاً)
# --------------------------
if not حالة_الاشتراك:
    st.sidebar.error(رسالة_الاشتراك)
    st.title("🔒 التطبيق مقفل - يلزم اشتراك شهري للوصول")
    st.warning("عذراً، هذا التطبيق مدفوع. يرجى اختيار إحدى طرق الدفع أدناه لإتمام الاشتراك والحصول على مفتاح التفعيل.")

    st.markdown("---")
    st.subheader("💳 طرق الدفع المتاحة للاشتراك الشهري")

    col_pay1, col_pay2, col_pay3 = st.columns(3)

    with col_pay1:
        st.markdown("### 🏦 1. التحويل البنكي (المحلي والدولي)")
        st.info(
            "**اسم البنك:** مصرف الراجحي / الإنماء\n\n"
            "**رقم الحساب:** SA0380000#################\n\n"
            "**رقم الايبان (IBAN):** SA03800000000000000000\n\n"
            "**اسم المستفيد:** شركة زازا للتجارة والتقنية"
        )

    with col_pay2:
        st.markdown("### 🌐 2. العملات الرقمية (USDT)")
        st.success(
            "**الشبكة:** TRC20 (Tron)\n\n"
            "**العنوان:**\n"
            "`TYourUSDTWalletAddressHere123456789`\n\n"
            "*يرجى إرسال لقطة شاشة لعملية التحويل مع عنوان المحفظة.*"
        )

    with col_pay3:
        st.markdown("### 💳 3. بطاقات الدفع الإلكتروني")
        st.warning(
            "**مدى / فيزا / ماستركارد / باي بال**\n\n"
            "للحصول على رابط الدفع السريع بالبطاقة، يرجى التواصل مباشرة عبر وسائل الدعم لإرسال الفاتورة."
        )

    st.markdown("---")
    st.subheader("📝 تأكيد عملية الدفع وإرسال طلب المفتاح")
    with st.form("form_payment"):
        f_name = st.text_input("الاسم الكامل")
        f_phone = st.text_input("رقم الواتساب لاستلام المفتاح (مع رمز الدولة)")
        f_method = st.selectbox("طريقة الدفع المستخدمة", ["التحويل البنكي", "العملات الرقمية USDT", "بطاقة ائتمانية / مدى"])
        f_note = st.text_area("معلومات إضافية أو رقم عملية التحويل / الحوالة")
        
        submit_btn = st.form_submit_button("إرسال طلب التفعيل")
        if submit_btn:
            if f_name and f_phone:
                st.success("تم استلام طلبك بنجاح! سيتم مراجعة الدفع وإرسال مفتاح الاشتراك الشهري عبر واتساب خلال دقائق.")
            else:
                st.error("الرجاء تعبئة الاسم ورقم الواتساب على الأقل.")

    st.stop()

# --------------------------
# دوال التطبيق للمشتركين المعتمدين
# --------------------------
st.sidebar.success(رسالة_الاشتراك)
st.sidebar.markdown("---")

@st.cache_data(ttl=60)
def جلب_بيانات(رمز, فترة):
    فترة_تغطية = "5d" if فترة in ["1m", "5m", "15m", "30m"] else "1mo"
    بيانات = yf.download(رمز, period=فترة_تغطية, interval=فترة, progress=False)
    if isinstance(بيانات.columns, pd.MultiIndex):
        بيانات.columns = بيانات.columns.get_level_values(0)
    return بيانات if not بيانات.empty else None

def حساب_مؤشرات(بيانات):
    df = بيانات.copy()
    df['RSI'] = RSIIndicator(close=df['Close'], window=14).rsi()
    ماكد = MACD(close=df['Close'])
    df['MACD'] = ماكد.macd()
    df['MACD_خط_اشارة'] = ماكد.macd_signal()
    df['EMA20'] = EMAIndicator(close=df['Close'], window=20).ema_indicator()
    df['EMA50'] = EMAIndicator(close=df['Close'], window=50).ema_indicator()
    بولينجر = BollingerBands(close=df['Close'])
    df['بولينجر_علوي'] = بولينجر.bollinger_hband()
    df['بولينجر_متوسط'] = بولينجر.bollinger_mavg()
    df['بولينجر_سفلي'] = بولينجر.bollinger_lband()
    ستوك = StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'])
    df['ستوك_K'] = ستوك.stoch()
    df['ستوك_D'] = ستوك.stoch_signal()
    return df.dropna(subset=['RSI', 'MACD', 'EMA20'])

def توليد_اشارات(بيانات):
    df = بيانات.copy()
    شروط_شراء = (
        ((df['RSI'] < 38) | (df['Close'] <= df['بولينجر_سفلي'])) & 
        ((df['MACD'] > df['MACD_خط_اشارة']) | (df['ستوك_K'] > df['ستوك_D']))
    )
    شروط_بيع = (
        ((df['RSI'] > 62) | (df['Close'] >= df['بولينجر_علوي'])) & 
        ((df['MACD'] < df['MACD_خط_اشارة']) | (df['ستوك_K'] < df['ستوك_D']))
    )
    df['منطقة_الدخول'] = 'انتظار ⚪'
    df.loc[شروط_شراء, 'منطقة_الدخول'] = 'منطقة شراء قوية (Call) 🟢'
    df.loc[شروط_بيع, 'منطقة_الدخول'] = 'منطقة بيع قوية (Put) 🔴'
    return df

def رسم_شارت(بيانات):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=بيانات.index, open=بيانات.Open, high=بيانات.High,
        low=بيانات.Low, close=بيانات.Close, name="السعر"
    ))
    fig.add_trace(go.Scatter(x=بيانات.index, y=بيانات.EMA20, name="متوسط 20", line=dict(color='blue', width=1.5)))
    fig.add_trace(go.Scatter(x=بيانات.index, y=بيانات.EMA50, name="متوسط 50", line=dict(color='orange', width=1.5)))
    fig.add_trace(go.Scatter(x=بيانات.index, y=بيانات.بولينجر_علوي, name="بولينجر علوي", line=dict(color='gray', width=1, dash='dot')))
    fig.add_trace(go.Scatter(x=بيانات.index, y=بيانات.بولينجر_سفلي, name="بولينجر سفلي", line=dict(color='gray', width=1, dash='dot'), fill='tonexty'))
    fig.update_layout(title="الرسم البياني مع مناطق التداول والمؤشرات", yaxis_title="السعر", xaxis_rangeslider_visible=False, template="plotly_dark", height=550)
    return fig

# --------------------------
# الواجهة الرئيسية (للمشتركين)
# --------------------------
st.title("📊 محلل التداول الذكي - النسخة المدفوعة VIP")
st.markdown("مرحباً بك في نسختك المفعلة. استمتع بالتحليل الفني المتقدم والتنبيهات الفورية.")

st.sidebar.header("إعدادات التحليل والاتصال")

# قائمة منسدلة بالأصول الشهيرة
قائمة_الأصول = {
    "يورو / دولار (EURUSD=X)": "EURUSD=X",
    "جنيه استرليني / دولار (GBPUSD=X)": "GBPUSD=X",
    "دولار / ين ياباني (USDJPY=X)": "USDJPY=X",
    "استرليني / ين (GBPJPY=X)": "GBPJPY=X",
    "بيتكوين / دولار (BTC-USD)": "BTC-USD",
    "إيثيريوم / دولار (ETH-USD)": "ETH-USD",
    "الذهب / دولار (GC=F)": "GC=F",
    "أصل مخصص (إدخال يدوي)": "CUSTOM"
}

اختيار_الأصل = st.sidebar.selectbox("اختر الأصل أو العملة", list(قائمة_الأصول.keys()))

if اختيار_الأصل == "أصل مخصص (إدخال يدوي)":
    رمز_العملة = st.sidebar.text_input("أدخل رمز الأصل يدوياً (مثال: AUDUSD=X)", value="EURUSD=X")
else:
    رمز_العملة = قائمة_الأصول[اختيار_الأصل]

الإطار_الزمني = st.sidebar.selectbox("الإطار الزمني", ["1m", "5m", "15m", "30m", "1h", "1d"], index=1)

st.sidebar.markdown("---")
st.sidebar.header("إعدادات واتساب")
رقم_الهاتف = st.sidebar.text_input("رقم الهاتف (مع رمز الدولة، مثال: +9665xxxxxxxx)", value="")
تفعيل_واتساب = st.sidebar.checkbox("تفعيل إرسال التنبيهات عبر واتساب تلقائياً")

if st.sidebar.button("تحليل السوق"):
    with st.spinner("جاري جلب البيانات وتحديد مناطق التداول..."):
        raw_data = جلب_بيانات(رمز_العملة, الإطار_الزمني)
        if raw_data is not None and not raw_data.empty:
            df_processed = حساب_مؤشرات(raw_data)
            if not df_processed.empty:
                df_signals = توليد_اشارات(df_processed)
                st.success("تم تحليل السوق وتحديد المناطق بنجاح!")
                st.plotly_chart(رسم_شارت(df_signals), use_container_width=True)
                
                st.subheader("🎯 التوصية الحالية ومنطقة الدخول")
                آخر_صف = df_signals.iloc[-1]
                الحالة = آخر_صف.get('منطقة_الدخول', 'انتظار ⚪')
                سعر_الحالي = آخر_صف.get('Close', 0)
                rsi_val = آخر_صف.get('RSI', 0)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("السعر الحالي", f"{سعر_الحالي:.4f}")
                col2.metric("مؤشر RSI", f"{rsi_val:.2f}")
                col3.metric("مؤشر MACD", f"{آخر_صف.get('MACD', 0):.4f}")
                col4.metric("حالة السوق", الحالة)
                
                رسالة = f"🚨 *تنبيه توصية تداول جديدة (VIP)*\n\n" \
                        f"📈 الأصل: {رمز_العملة}\n" \
                        f"⏱ الإطار: {الإطار_الزمني}\n" \
                        f"🎯 الحالة: {الحالة}\n" \
                        f"💵 السعر الحالي: {سعر_الحالي:.4f}\n" \
                        f"📊 مؤشر RSI: {rsi_val:.2f}\n" \
                        f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
                if "شراء" in الحالة:
                    st.success("### 🟢 الفرصة الحالية: صفقة صعود (Call) مقترحة")
                elif "بيع" in الحالة:
                    st.error("### 🔴 الفرصة الحالية: صفقة هبوط (Put) مقترحة")
                else:
                    st.info("### ⚪ السوق في نطاق عرضي (انتظار)")

                if تفعيل_واتساب and رقم_الهاتف and ("شراء" in الحالة or "بيع" in الحالة):
                    try:
                        now = datetime.now()
                        hour = now.hour
                        minute = now.minute + 1
                        if minute >= 60:
                            minute = 0
                            hour = (hour + 1) % 24
                        kit.sendwhatmsg(رقم_الهاتف, رسالة, hour, minute, wait_time=15, tab_close=True)
                        st.sidebar.success("تم إرسال التنبيه عبر واتساب بنجاح! 📱")
                    except Exception as e:
                        st.sidebar.error(f"خطأ في إرسال واتساب: {e}")
            else:
                st.warning("البيانات المسترجعة غير كافية لحساب المؤشرات. جرب إطاراً زمنياً أكبر مثل 1h.")
        else:
            st.error("عذراً، لم يتم العثور على بيانات لهذا الرمز. تأكد من صحة الرمز.")